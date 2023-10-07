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


class DamageTracker:

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
        self.path_to_images = 'input/playerDamage'

    def track_damage(self, queued_image, end):
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
                             headers=["Frame", "Damage"], name='Player Damage')
        end.value = True

    def crop_to_first_white_line(self, thresh):
        #todo: implement
        pass

    def process_result(self, result_OCR, pbar):
        for bbox, text, prob in result_OCR:
            damage_found = int(text)
            if prob > 0.93 and self.is_valid_damage(damage_found, pbar):
                self.match_count += 1
                self.results.append(damage_found)
                self.result_image_number.append(self.loop_number)
                pbar.set_description(desc=str(self.match_count), refresh=True)
                return True
        return False

    def is_valid_damage(self, damage, pbar):
        if self.results[-1] > damage or self.results[-1] + 400 < damage:
            pbar.write(f'Bad match, found {damage} but expected closer to '
                       f'{self.results[-1]} at image {self.loop_number}')
            return False
        return True

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
