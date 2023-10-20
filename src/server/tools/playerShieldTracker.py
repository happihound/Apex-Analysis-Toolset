import cv2
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
from tqdm import tqdm
from util.apexUtils import ApexUtils as util


class ShieldTracker:

    __slots__ = ['end', 'queued_image', 'frame_number', 'match_count',
                 'results', 'result_image_number', 'path_to_images', 'apex_utils', 'path']

    def __init__(self, path):
        self.queued_image = None
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util()
        self.path = path
        self.path_to_images = util().get_path_to_images() + path

    def track_shield(self, queued_image, end) -> None:
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        with tqdm(files) as pbar:
            for file in pbar:
                self.frame_number = self.apex_utils.extract_frame_number(file)
                image = cv2.imread(file)
                result = self.parse_shield(image)
                self.queued_image.put(image)
                if result != -1:
                    self.match_count += 1
                    self.results.append(result)
                    self.result_image_number.append(self.frame_number)
                    self.queued_image.put(image)
                else:
                    self.queued_image.put(image)
                    self.results.append(self.results[-1])
                    self.result_image_number.append(self.frame_number)

        end.value = 1
        self.results = self.filter_values(self.results)
        self.save_results()
        # self.display_graph()

    @staticmethod
    def round_shield(shield: float) -> int:
        if shield > 120:
            shield = 125
        if shield < 5:
            shield = 0
        return shield

    def parse_shield(self, image: np.ndarray) -> int:
        scale_factor = 5
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        lower_bound = np.array([0, 0, 220])
        upper_bound = np.array([220, 255, 255])
        dim = (width, height)

        # Resize the image
        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

        # Color segmentation
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        segmented = cv2.bitwise_and(resized, resized, mask=mask)

        # Convert to grayscale and apply thresholding
        gray = cv2.cvtColor(segmented, cv2.COLOR_BGR2GRAY)
        blurred = cv2.blur(gray, (25, 50))
        blurred = cv2.medianBlur(blurred, 151)
        _, thresholded = cv2.threshold(blurred, 20, 255, cv2.THRESH_BINARY)
        self.queued_image.put(thresholded)

        # Find contours
        contours, _ = cv2.findContours(thresholded, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return -1  # No shield detected

        # Extract the largest contour (assuming it's the shield)
        contour = max(contours, key=cv2.contourArea)

        # Filter small contours, which are probably noise
        if cv2.contourArea(contour) <= 600:
            return -1

        # Get enclosing circle and calculate shield width
        _, radius = cv2.minEnclosingCircle(contour)
        shield_width = radius * 2
        shield_value = self.round_shield((shield_width / width) * 125)

        return int(shield_value)

    def filter_values(self, values):
        new_values = [values[0]]

        # Iterate over the values, skipping the first and last ones
        for i in range(1, len(values) - 1):
            # If the previous and next values are the same, set the current value to the previous value
            if values[i - 1] == values[i + 1]:
                new_values.append(values[i - 1])
            else:
                new_values.append(values[i])
        new_values.append(values[-1])
        return new_values

    def save_results(self) -> None:
        self.apex_utils.save(data=self.results, frame=self.result_image_number,
                             headers=["Frame", "Shield"], name=self.path[1:])

    def main(self) -> None:
        print('Starting player shield tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Health Tracker')
        self.track_shield(queued_image, end)
        print('Finished player shield tracker')


if __name__ == "__main__":
    health_tracker = ShieldTracker('/playerShield')
    health_tracker.main()
