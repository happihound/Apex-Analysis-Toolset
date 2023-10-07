import time
import cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import easyocr
from tqdm import tqdm
from util.apexUtils import ApexUtils as util
import numpy as np

plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"


class evoTracker:

    __slots__ = ['end', 'queued_image', 'loop_number', 'match_count',
                 'results', 'result_image_number', 'reader', 'path_to_images', 'apex_utils']

    def __init__(self):
        self.end = 0
        self.queued_image = None
        self.loop_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.reader = None
        self.apex_utils = util.ApexUtils()
        self.path_to_images = 'input/playerEvo'

    def track_evo(self, queued_image, end):
        self.reader = easyocr.Reader(['en'])
        self.end = end
        self.queued_image = queued_image
        files = glob.glob(self.path_to_images + '/*.png')
        with tqdm(files) as pbar:
            for file in pbar:
                image = cv2.imread(file)
                self.loop_number += 1
                result_OCR = self.reader.readtext(image, allowlist='0123456789', paragraph=False)
                if self.process_result(result_OCR, pbar):
                    self.queued_image.put(image)
        self.filter_Values(self.results)
        print(f'found {self.match_count} total matches')
        self.apex_utils.save(data=self.results, frame=self.result_image_number,
                             headers=["Frame", "Evo"], name='Evo')
        end.value = True

    def process_result(self, result_OCR, pbar):
        for bbox, text, prob in result_OCR:
            if text == '':
                continue
            evo_found = int(text)
            if prob > 0.93 and self.is_valid_evo(evo_found):
                self.match_count += 1
                self.results.append(evo_found)
                self.result_image_number.append(self.loop_number)
                try:
                    pbar.set_description(desc=str(self.match_count), refresh=True)
                except:
                    pass
                return True
        return False

    def is_valid_evo(self, evo_found):
        if (evo_found > 750):
            return False
        if (evo_found < 0):
            return False
        if (evo_found == 0):
            return False
        return True

    def filter_Values(self, values):
        # Make a copy of the list to avoid changing the original
        newValues = values.copy()
        # Loop through the list, skipping the first and last values
        for i in range(1, len(values) - 1):
            # If the next value is the same as the previous value, set the current value to that value
            if values[i - 1] == values[i + 1]:
                newValues[i] = values[i - 1]
            self.match_count = len(newValues)
        # Return the new list
        self.results = newValues

    def main(self):
        print('Starting evo tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Evo Tracker')
        self.track_evo(queued_image, end)
        print('Finished evo tracker')


if __name__ == '__main__':
    evoTracker = evoTracker()
    evoTracker.main()
