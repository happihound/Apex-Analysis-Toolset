import time
import cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import easyocr
from tqdm import tqdm
import ApexUtils
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
        self.apex_utils = ApexUtils.ApexUtils()
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
        print(f'found {self.match_count} total matches')
        self.apex_utils.save(data=self.results, frame=self.result_image_number,
                             headers=["Frame", "Evo"], name='Evo')
        end.value = True

    def process_result(self, result_OCR, pbar):
        for bbox, text, prob in result_OCR:
            evo_found = int(text)
            if prob > 0.93 and self.is_valid_damage(evo_found, pbar):
                self.match_count += 1
                self.results.append(evo_found)
                self.result_image_number.append(self.loop_number)
                pbar.set_description(desc=str(self.match_count), refresh=True)
                return True
        return False

    def is_valid_evo(self, evo_found, pbar):
        if self.results[-1] > evo_found or self.results[-1] + 400 < evo_found:
            pbar.write(f'Bad match, found {evo_found} but expected closer to '
                       f'{self.results[-1]} at image {self.loop_number}')
            return False
        return True
    
    def filterValues(values):
        # Make a copy of the list to avoid changing the original
        newValues = values.copy()

        # Loop through the list, skipping the first and last values
        for i in range(1, len(values) - 1):
            # If the next value is the same as the previous value, set the current value to that value
            if values[i - 1] == values[i + 1]:
                newValues[i] = values[i - 1]

        # Return the new list
        return newValues


def check_match(result, loopNumber, foundData, imageNumber, pbar, matchCount):
    # For each result in the result list
    for (bbox, text, prob) in result:
        # If there is no text ignore it
        if not text:
            continue
        # Convert the text to a number
        evoFound = int(text)
        # Needs at 98% or great probability of being accurate
        if (prob > 0.98):
            # Max value of an EVO
            if (evoFound > 751):
                print('bad match, over 750')
                continue
            # Update the progress bar
            pbar.set_description(desc=str(matchCount), refresh=True)
            # Add the data to the lists
            foundData.append(evoFound)
            imageNumber.append(loopNumber)
            # Return true to say we found a match
            return True
    # Return false to say we didn't find a match
    return False

    def main(self):
        print('Starting damage tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Damage Tracker')
        self.track_damage(queued_image, end)
        print('Finished damage tracker')


if __name__ == '__main__':
    damage_tracker = DamageTracker()
    damage_tracker.main()
