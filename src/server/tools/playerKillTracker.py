import csv
import threading
import cv2
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
from tqdm import tqdm
from util.apexUtils import ApexUtils as util

plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"


class KillTracker:
    __slots__ = ['end', 'queued_image', 'frame_number', 'match_count',
                 'results', 'result_image_number', 'path_to_images', 'apex_utils', 'rolling_array', 'stop_event', 'running_thread', 'socketio']

    def __init__(self):
        self.stop_event = threading.Event()
        self.socketio = None
        self.running_thread = None
        self.queued_image = None
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util()
        self.path_to_images = util().get_path_to_images() + "/playerKills"
        self.rolling_array = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1]

    def set_socketio(self, socketio):
        self.socketio = socketio

    def track_kills(self, queued_image, end) -> None:
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        with tqdm(files) as pbar:
            for file in pbar:
                if self.check_stop():
                    end.value = 1
                    break
                image = cv2.imread(file)
                image = self.crop_icon_dynamic(image)
                self.frame_number = self.apex_utils.extract_frame_number(file)
                image = self.load_and_preprocess_image(image)
                result = self.apex_utils.extract_numbers_from_image(image=image)

                if self.process_result(result, pbar):
                    self.queued_image.put(image)
                else:
                    self.results.append(self.results[-1])
                    self.result_image_number.append(self.frame_number)

        print(f'found {self.match_count} total matches')
        end.value = 1
        self.results = KillTracker().filter_values(self.results)
        self.apex_utils.save(data=self.results, frame=self.result_image_number,
                             headers=["Frame", "Kills"], name='Player Kills')

    def process_result(self, result, pbar) -> bool:
        if len(result) == 0:
            return False
        for (_, text, prob) in result:
            if text == '':
                continue
            text = int(text)

            check_value = int((np.sum(self.rolling_array[-3:-1])/2))
           # print('\n\n'+str(check_value) + ' ' + str(text)+'\n\n\n\n')
            if text > 27:
                continue
            self.rolling_array.append(text)
            if check_value > text or check_value + 5 < text:
                continue

            self.match_count += 1
            self.results.append(text)
            self.result_image_number.append(self.frame_number)
            pbar.set_description(desc=str(self.match_count), refresh=True)
            return True
        return False

    def load_and_preprocess_image(self, image: str) -> np.ndarray:
        thresholded_image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        resized = cv2.resize(thresholded_image, (0, 0), fx=5, fy=5)
        return resized

    def crop_icon_dynamic(self, image):
        '''
        This method crops the image to not contain the damage icon
        image: the image to be cropped
        returns: the cropped image
        '''
        # Convert image to grayscale if it isn't already
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Blur horizontally
        blurred = cv2.GaussianBlur(image, (1, 15), 0)

        # Threshold the image
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Identify the position with more than 2 consecutive black columns
        black_columns_count = 0
        start_col = 0
        for col in range(thresh.shape[1]):
            if np.all(thresh[:, col] == 0):  # Check if the column is entirely black
                black_columns_count += 1
                if col > image.shape[1] / 2:
                    break
                if black_columns_count > 2:
                    start_col = col
                    break
            else:
                black_columns_count = 0  # Reset count if a non-black column is found

        # Crop everything after the detected region
        final_cropped = image[:, start_col:]
        return final_cropped

    @staticmethod
    def most_frequent(lst):
        return max(set(lst), key=lst.count)

    @staticmethod
    def replace_lesser_values(values):
        i = 0
        last_valid_value = None  # To store the last valid value before encountering x

        while i < len(values):
            x = values[i]
            x_count = 0
            j = i

            # Count the occurrences of x
            while j < len(values) and values[j] == x:
                x_count += 1
                j += 1

            # Check for the next number that's >= x
            lesser_values = []  # To store values lesser than x
            while j < len(values) and values[j] < x:
                lesser_values.append(values[j])
                j += 1

            if len(lesser_values) > x_count:
                # If we have more lesser values than occurrences of x
                for k in range(i, i + x_count):
                    values[k] = last_valid_value  # Replace with last valid value
                i = i + x_count
            else:
                # Save x as the last valid value and continue to the next different number
                last_valid_value = x
                i = j

        return values

    @staticmethod
    def ensure_increasing(values):
        last_highest = 0
        return_values = []
        for value in values:
            if value < last_highest:
                return_values.append(last_highest)
            else:
                return_values.append(value)
                last_highest = value
        return return_values

    @staticmethod
    def filter_values(values):
        values = KillTracker().replace_lesser_values(values)
        values = KillTracker().ensure_increasing(values)
        return values

    def start_in_thread(self):
        if self.running_thread and self.running_thread.is_alive():
            print("Kill tracker is already running")
            return
        self.stop_event.clear()
        self.running_thread = threading.Thread(target=self.main)
        self.running_thread.start()

    def check_stop(self):
        if self.stop_event.is_set():
            print("Stopping kill tracker")
            print('!WEBPAGE! !TOGGLE!')
            return True
        return False

    def stop(self):
        self.stop_event.set()

    def main(self):
        print('!WEBPAGE! !TOGGLE!')
        print('Starting kill tracker')
        end = multiprocessing.Value("i", False)
        self.queued_image = multiprocessing.Queue()
        self.apex_utils.display(self.queued_image, end, 'kill-tracker', self.socketio)
        self.track_kills(self.queued_image, end)
        print('Finished kill tracker')
        print('!WEBPAGE! !TOGGLE!')


if __name__ == '__main__':
    tracker = KillTracker()
    tracker.main()
