import cv2
import multiprocessing
from tqdm import tqdm
from util.apexUtils import ApexUtils as util
import numpy as np
ALLOWED_DAMAGE_DIFF = 400  # max difference between damage values

'''
This class is responsible for tracking the damage dealt by the player,
it uses OCR to extract the ammount of damage.
it uses filtering to remove any damage over or under 400, as a window for allowable damage delta.
It uses the following from the ApexUtils class:
    - reader
    - display
    - save
    - load_files_from_directory
    - extract_frame_number
    - get_path_to_images
    - extract_numbers_from_image

The result of this class is saved in a csv file with the following headers:
    - Frame
    - damage
This describes the frame number and the damage dealt up to that frame.
'''


class DamageTracker:
    __slots__ = ['end', 'queued_image', 'frame_number', 'match_count',
                 'results', 'result_image_number', 'path_to_images', 'apex_utils']

    def __init__(self) -> None:
        self.queued_image = None
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util()
        self.path_to_images = util().get_path_to_images()+"/playerDamage"

    def track_damage(self, queued_image, end) -> None:
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        with tqdm(files) as pbar:
            for file in pbar:
                self.frame_number = self.apex_utils.extract_frame_number(file)
                image = self.load_and_preprocess_image(file)
                image = self.crop_icon_dynamic(image)
                result_OCR = self.apex_utils.extract_numbers_from_image(image)

                if self.process_result(result_OCR, pbar):
                    self.queued_image.put(image)

        # print(f'found {self.match_count} total matches')
        self.apex_utils.save(data=self.results, frame=self.result_image_number,
                             headers=["Frame", "Damage"], name='Player Damage')
        end.value = 1

    def load_and_preprocess_image(self, file_path: str) -> np.ndarray:
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError(f"Failed to load image from {file_path}")

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresholded_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return thresholded_image

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

    def process_result(self, result_OCR, pbar):
        '''
        This method processes the result of the OCR, it checks if the result is valid and if it is it adds it to the results
        result_OCR: the result of the OCR
        pbar: the progress bar to be updated
        returns: True if the result is valid, False otherwise
        '''
        for _, text, prob in result_OCR:
            damage_found = int(text)
            if prob > 0.93 and self.is_valid_damage(damage_found, pbar):
                self.match_count += 1
                self.results.append(damage_found)
                self.result_image_number.append(self.frame_number)
                pbar.set_description(desc=str(self.match_count), refresh=True)
                return True
            else:
                self.results.append(self.results[-1])
                self.result_image_number.append(self.frame_number)
        return False

    def is_valid_damage(self, damage, pbar) -> bool:
        '''
        This method checks if the damage is valid, it checks if the damage is within the allowed damage delta
        damage: the damage to be checked
        pbar: the progress bar to be updated
        returns: True if the damage is valid, False otherwise
        '''
        if self.results[-1] > damage or self.results[-1] + 400 < damage:
            # pbar.write(f'Bad match, found {damage} but expected closer to '
            #            f'{self.results[-1]} at image {self.frame_number}')
            return False
        return True

    def main(self) -> None:
        print('Starting damage tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Damage Tracker')
        self.track_damage(queued_image, end)
        print('Finished damage tracker')


if __name__ == '__main__':
    damage_tracker = DamageTracker()
    damage_tracker.main()
