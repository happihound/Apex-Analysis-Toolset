import numpy as np
import cv2
import matplotlib.pyplot as plt
import multiprocessing
import easyocr
from statsmodels.nonparametric.smoothers_lowess import lowess
from tqdm import tqdm
from util.apexUtils import ApexUtils as util


class UltTracker:

    __slots__ = ['path_to_images', 'queued_image', 'end', 'apex_utils',
                 'frame_number', 'match_count', 'results', 'result_image_number']

    def __init__(self):
        self.queued_image = None
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util()
        self.path_to_images = util().get_path_to_images() + "/playerUlt"

    def track_ult(self, queued_image, end) -> None:
        self.end = end
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        for file in tqdm(files):
            self.frame_number = self.apex_utils.extract_frame_number(file)
            image = cv2.imread(file)
            # readtext(image, allowlist='0123456789secSEC', paragraph=False)
            result = self.apex_utils.extract_text_from_image(image)
            self.process_result(result)
            self.queued_image.put(image)

        self.results = self.filter_values(self.results)

        end.value = 1
        self.graph_filter_and_save(self.result_image_number, self.results)

    def process_result(self, result) -> None:
        if len(result):
            for (bbox, text, prob) in result:
                if text == '':
                    continue
                # Remove unwanted text
                if '%' in text or 'S' in text or 's' in text:
                    # print('\n')
                    # print(text)
                    # print('\n')
                    clean_text = ''.join(ch for ch in text if ch.isdigit())
                    if clean_text == '':
                        continue
                    text = int(clean_text)
                    if text > 100 or text < 0:
                        continue
                    self.match_count += 1
                    self.results.append(text)
                    self.result_image_number.append(self.frame_number)
                    return
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

    def graph_filter_and_save(self, frame_number, results) -> None:
        self.apex_utils.save(results, frame_number, ["Frame", "Utl Cooldown"], 'Player Utl Cooldown')
        return
        plt.plot(x, y)
        plt.xlabel("Time")
        plt.ylabel("Cool Down")
        plt.xlim([0, len(frame_number)])
        plt.show()
        plt.pause(99999)

    def main(self) -> None:
        print('Starting ult tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Utl Tracker')
        self.track_ult(queued_image, end)
        print('Finished ult tracker')


if __name__ == '__main__':
    ult_tracker = UltTracker()
    ult_tracker.main()
