import matplotlib.pyplot as plt
import multiprocessing
from tqdm import tqdm
import jellyfish
from util.apexUtils import ApexUtils as util
import numpy as np
import cv2
import easyocr

plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"

'''
This class is responsible for tracking the gun of the player,
it uses OCR to extract the gun name.
It uses a word similarity checker to determine the most likely gun name.
It uses the following from the ApexUtils class:
    - display
    - save
    - load_files_from_directory
    - extract_frame_number
    - get_path_to_images
    - extract_numbers_from_image

The result of this class is saved in a csv file with the following headers:
    - Frame
    - Gun
This describes the frame number and the guns detected on that frame.
'''


class GunTracker:
    __slots__ = ['path_to_images', 'queued_image', 'end', 'apex_utils',
                 'frame_number', 'match_count', 'results', 'result_image_number', 'apex_utils']

    def __init__(self):
        self.queued_image = None
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util()
        self.path_to_images = self.apex_utils.get_path_to_images() + "/playerGuns"

    def track_gun(self, queued_image, end) -> None:
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        # Possible gun names
        gun_List = ['R-301', 'HEMLOK', 'FLATLINE', 'HAVOC', 'SPITFIRE', 'DEVOTION', 'RAMPAGE', 'L-STAR', 'BOCEK', 'G7 SCOUT', 'TRIPLE TAKE', '30-30', 'PEACEKEEPER',
                    'MASTIFF', 'EVA-8', 'MOZAMBIQUE', 'CAR', 'R-99', 'PROWLER', 'VOLT', 'ALTERNATOR', 'WINGMAN', 'RE-45', 'P2020', 'LONGBOW', 'SENTINEL', 'KRABER', 'CHARGE RIFLE', 'NEMESIS']

        with tqdm(files) as pbar:
            for file in pbar:
                self.frame_number = self.apex_utils.extract_frame_number(file)
                image = cv2.imread(file)  # Consider moving this to apexUtils
                result = self.apex_utils.extract_text_from_image(image)

                if len(result) == 2:
                    for (bbox, text, prob) in result:
                        found_gun = self.gun_similarity_checker(gun_List, text)
                        if found_gun != 0:
                            self.match_count = self.match_count + 1
                            self.results.append(found_gun)
                            self.result_image_number.append(self.frame_number)
                            pbar.set_description(desc=str(self.match_count), refresh=True)
                        else:
                            self.results.append(self.results[-1])
                            self.result_image_number.append(self.frame_number)
                        self.queued_image.put(image)

        print(f'found {self.match_count} total matches')
        self.graph_filter_and_save()
        end.value = 1

    def graph_filter_and_save(self) -> None:
        # to-do graphing
        filtered_data = self.filter_values()
        self.apex_utils.save(filtered_data, self.result_image_number,
                             ["Frame", "Gun"], 'Player Guns')
        print('DONE MATCHING')

    def gun_similarity_checker(self, guns, inputString):
        inputString = inputString.upper()
        largestProbValue = 0
        predictedGun = 0
        for gun in guns:
            gunSimlarity = (self.similar(gun, inputString))
            if gunSimlarity > largestProbValue:
                largestProbValue = gunSimlarity
                predictedGun = gun
        return predictedGun

    def similar(self, inputStringOne, inputStringTwo):
        similarity = jellyfish.jaro_winkler_similarity(
            inputStringOne, inputStringTwo)
        # if len(inputStringOne) == len(inputStringTwo) or len(inputStringOne) == len(inputStringTwo) - 1 or len(inputStringOne) == len(inputStringTwo) + 1:
        #     similarity = similarity + 0.1
        # else:
        #     similarity = similarity - 0.2
        # return similarity
        return similarity

    def filter_values(self):
        # Step 1: Initial filtering based on neighboring values
        values = self.results
        newValues = values.copy()
        for i in range(1, len(values) - 1):
            if values[i - 1] == values[i + 1]:
                newValues[i] = values[i - 1]

        # Step 2: De-noising based on frequency
        lii_unique = list(set(newValues))
        counts = [newValues.count(value) for value in lii_unique]

        for index, absoluteCount in enumerate(counts):
            if ((absoluteCount / len(newValues) * 100) <= 1.5):
                value_to_remove = lii_unique[index]
                while value_to_remove in newValues:
                    removal_index = newValues.index(value_to_remove)
                    newValues.pop(removal_index)
                    self.result_image_number.pop(removal_index)

        return newValues

    def main(self) -> None:
        print('Starting gun tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Gun Tracker')
        self.track_gun(queued_image, end)
        print('Finished damage tracker')


if __name__ == '__main__':
    gun_finder = GunTracker()
    gun_finder.main()
