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
                 'results', 'result_image_number', 'path_to_images', 'apex_utils', 'rolling_array']

    def __init__(self):
        self.queued_image = None
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util()
        self.path_to_images = util().get_path_to_images() + "/playerKills"
        self.rolling_array = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1]

    def track_kills(self, queued_image, end) -> None:
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        with tqdm(files) as pbar:
            for file in pbar:
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
    def filter_values(values):
        loop_number = 8
        new_values = values.copy()
        for i in values:
            loop_number += 1
            if loop_number > len(values) - 4:
                break
            new_values[loop_number] = KillTracker.most_frequent(values[loop_number-8:loop_number+4])
        return new_values

    @staticmethod
    def most_frequent(lst):
        return max(set(lst), key=lst.count)

    def main(self):
        print('Starting kill tracker')
        end = multiprocessing.Value("i", False)
        self.queued_image = multiprocessing.Queue()
        self.apex_utils.display(self.queued_image, end, 'Kill Tracker')
        self.track_kills(self.queued_image, end)
        print('Finished kill tracker')


if __name__ == '__main__':
    tracker = KillTracker()
    tracker.main()
