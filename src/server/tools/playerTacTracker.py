import threading
import numpy as np
import cv2
import matplotlib.pyplot as plt
import multiprocessing
from statsmodels.nonparametric.smoothers_lowess import lowess
from tqdm import tqdm
from src.util.apexUtils import ApexUtils as util


class TacTracker:

    __slots__ = ['path_to_images', 'queued_image', 'end', 'apex_utils',
                 'frame_number', 'match_count', 'results', 'result_image_number', 'stop_event', 'running_thread', 'socketio', 'path']

    def __init__(self, socketio):
        self.queued_image = None
        self.stop_event = threading.Event()
        self.socketio = socketio
        self.running_thread = None
        self.end = None
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util(socketio)
        self.path = "/playerTac"
        self.path_to_images = self.apex_utils.get_path_to_images() + "/playerTac"

    def track_tac(self, queued_image, end) -> None:
        self.end = end
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        with tqdm(files) as pbar:
            for file in pbar:
                if self.check_stop():
                    end.value = 1
                    break
                self.frame_number = self.apex_utils.extract_frame_number(file)
                image = cv2.imread(file)
                # readtext(image, allowlist='0123456789secSEC', paragraph=False)
                result = self.apex_utils.extract_text_from_image(image)
                self.process_result(result)
                self.queued_image.put(image)

        self.results = self.filter_values(self.results)
        print(f'!WEBPAGE! found {self.match_count} total matches')
        end.value = 1
        # self.graph_filter_and_save(self.result_image_number, self.results)

    def process_result(self, result) -> None:
        if len(result):
            for (bbox, text, prob) in result:
                if text == '':
                    continue
                # Remove unwanted text
                if 'sec' in text:
                    text = text.replace('s', '').replace('e', '').replace(
                        'c', '').replace('S', '').replace('E', '').replace('C', '')
                    clean_text = ''.join(ch for ch in text if ch.isdigit())
                    if clean_text == '':
                        continue
                    text = int(clean_text)
                    if text >= 45:
                        continue
                    self.match_count += 1
                    self.results.append(text)
                    self.result_image_number.append(self.frame_number)
        else:
            self.results.append(self.results[-1])
            self.result_image_number.append(self.frame_number)

    def filter_values(self, values):
        new_values = [values[0]]

        # Iterate over the values, skipping the first and last ones
        for i in range(1, len(values) - 1):
            # If the previous and next values are the same, set the current value to the previous value
            if values[i - 1] == values[i + 1]:
                new_values.append(values[i - 1])
            # Check if the value at i is over or under 10 from the previous and next values
            elif abs(values[i] - values[i - 1]) > 10 and abs(values[i] - values[i + 1]) > 10:
                # Replace the value at i with the average of the previous and next values
                new_values.append((values[i - 1] + values[i + 1]) // 2)
            else:
                new_values.append(values[i])
        new_values.append(values[-1])
        return new_values

    def save_results(self) -> None:
        self.apex_utils.save(data=self.results, frame=self.result_image_number,
                             headers=["Frame", "Tac"], name=self.path[1:])

    @staticmethod
    def smoothing(y, x):
        lowess_frac = 0.005
        y_smooth = lowess(y, x, is_sorted=False, frac=lowess_frac, return_sorted=False)
        return x, y_smooth

    def start_in_thread(self):
        if self.running_thread and self.running_thread.is_alive():
            print("!WEBPAGE! Tac tracker is already running")
            return
        self.stop_event.clear()
        self.running_thread = threading.Thread(target=self.main)
        self.running_thread.start()

    def check_stop(self):
        if self.stop_event.is_set():
            print("!WEBPAGE! Stopping tac tracker")
            return True
        return False

    def stop(self):
        self.stop_event.set()
        self.end.value = 1

    def main(self) -> None:
        print('!WEBPAGE! Starting tac tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'tac-tracker')
        self.track_tac(queued_image, end)
        print('!WEBPAGE! Finished tac tracker')


if __name__ == '__main__':
    tac_tracker = TacTracker()
    tac_tracker.main()
