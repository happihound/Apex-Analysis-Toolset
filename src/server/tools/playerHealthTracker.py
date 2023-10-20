import cv2
import numpy as np
import multiprocessing
from tqdm import tqdm
from util.apexUtils import ApexUtils as util


class HealthTracker:

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

    def track_health(self, queued_image, end) -> None:
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        with tqdm(files) as pbar:
            for file in pbar:
                self.frame_number = self.apex_utils.extract_frame_number(file)
                image = cv2.imread(file)
                result = self.parse_hp(image)
                self.queued_image.put(image)
                if result != -1:
                    self.match_count += 1
                    self.results.append(result)
                    self.result_image_number.append(self.frame_number)
                    self.queued_image.put(image)
                else:
                    self.results.append(self.results[-1])
                    self.result_image_number.append(self.frame_number)
                    self.queued_image.put(image)

        end.value = 1
        self.results = self.filter_values(self.results)
        self.save_results()
        # self.display_graph()

    @staticmethod
    def round_hp(health: float) -> int:
        if health > 99:
            health = 100
        if health < 3:
            health = 0
        return health

    def parse_hp(self, image: np.ndarray) -> int:
        scale_factor = 5
        lower_red = np.array([0, 0, 220])
        upper_red = np.array([180, 45, 255])

        # Resize the image for better accuracy.
        resized_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

        # Convert to HSV for better color segmentation.
        hsv = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)

        # Create a mask to segment the health bar.
        mask = cv2.inRange(hsv, lower_red, upper_red)

        # Find contours in the mask.
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return -1  # No contours found.

        # Get the largest contour which should be the health bar.
        main_contour = max(contours, key=cv2.contourArea)

        if cv2.contourArea(main_contour) <= 600:
            return -1  # Health bar contour is too small.

        # Extract bounding box of the main contour to get its width.
        x, y, w, h = cv2.boundingRect(main_contour)

        # Calculate health percentage based on width.
        health_percentage = self.round_hp((w / resized_image.shape[1]) * 100)

        # Check for downed player by using different color thresholds.
        lower_downed = np.array([60, 200, 190])
        upper_downed = np.array([160, 255, 215])
        mask_downed = cv2.inRange(hsv, lower_downed, upper_downed)

        # If the mask has significant white regions, it means the player is downed.
        if np.sum(mask_downed) > 200 * 255:  # Threshold can be adjusted based on observation.
            return 1

        return int(health_percentage)

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
                             headers=["Frame", "Health"], name=self.path[1:])

    def main(self) -> None:
        print('Starting player health tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Health Tracker')
        self.track_health(queued_image, end)
        print('Finished player health tracker')


if __name__ == "__main__":
    health_tracker = HealthTracker('/playerHealth')
    health_tracker.main()
