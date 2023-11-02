# cython: profile=True
import threading
import numpy as np
import cv2
import matplotlib.pyplot as plt
from src.util.apexUtils import ApexUtils as util
import multiprocessing
from tqdm import tqdm


class MiniMapPlotter:
    """
    Class to handle mini map image matching against a given game map.
    """

    __slots__ = ['map_name', 'game_image_ratio', 'game_map_image', 'mapKeyPoints', 'min_match_count',
                 'poly_tolerance', 'polysizeArray', 'featureMappingAlgMiniMap', 'featureMatcher',
                 'apex_utils', 'results', 'resultImageNumber', 'start_color', 'end_color', 'stop_event', 'running_thread', 'socketio', 'end', 'queued_image']

    def __init__(self, socketio, min_match_count=11, poly_tolerance=0.5, start_color=(0, 0, 255), end_color=(255, 0, 0)):
        """
        Initialize the MiniMapPlotter with the given parameters.

        Parameters:
        - given_map: Name of the map.
        - ratio: Image ratio.
        - min_match_count: Minimum number of matching key points between two images.
        - poly_tolerance: Tolerance for polygon size validation.
        """
        self.socketio = socketio
        self.running_thread = None
        self.end = None
        self.stop_event = threading.Event()
        self.start_color = np.array(start_color, dtype=np.float32)
        self.end_color = np.array(end_color, dtype=np.float32)
        self.apex_utils = util(socketio=socketio)
        self.map_name = None
        self.game_image_ratio = None
        self.game_map_image = None
        self.mapKeyPoints = None
        self.min_match_count = min_match_count
        self.poly_tolerance = poly_tolerance
        self.polysizeArray = [650000, 650000, 560000, 340000, 540000, 440000, 600000]
        self.featureMappingAlgMiniMap = cv2.SIFT_create()
        self.featureMatcher = cv2.BFMatcher_create(normType=cv2.NORM_L2SQR)
        self.results = []
        self.resultImageNumber = []

    def get_color(self, fraction):
        return tuple(np.round(self.start_color + fraction * (self.end_color - self.start_color)).astype(np.int32))

    def setup_map(self):
        """
        Set up the map for matching.
        """
        print("!WEBPAGE! Setting up map")
        self.load_map_key_points('src/server/internal/packedKeypoints/'+self.game_image_ratio+'/' +
                                 self.map_name+self.game_image_ratio+'KeyPoints.npy')
        self.game_map_image = cv2.imread('src/server/internal/maps/'+self.game_image_ratio +
                                         '/map'+self.map_name+self.game_image_ratio+'.jpg')
        print("!WEBPAGE! Map setup complete")

    def process_all_images(self):
        """
        Process all the mini map images.

        """
        print('!WEBPAGE! Starting matching')
        line = []
        file_timestamps = []
        files = self.apex_utils.load_files_from_directory(directory=self.apex_utils.get_path_to_images()+"/miniMap")

        for file in files:
            timestamp = self.apex_utils.extract_frame_number(file)
            file_timestamps.append(timestamp)

        min_time, max_time = min(file_timestamps), max(file_timestamps)
        # Loop through the mini map images
        with tqdm(files) as pbar:
            for idx, file in enumerate(pbar):
                if self.check_stop():
                    self.end.value = 1
                    break
                frame_number = self.apex_utils.extract_frame_number(file)
                # Load the mini map images
                # print(flush=True)
                # print("Computing Image " + file.split('\\')[1], end='\n\t')
                display_image = self.game_map_image
                center_point = self.process_image(file)
                if center_point is not False:
                    line.append(center_point)
                    fraction = (file_timestamps[idx] - min_time) / (max_time - min_time)
                    color = self.get_color(fraction)
                    display_image = self.edit_image(display_image, line, color)
                    self.resultImageNumber.append(frame_number)
                    self.results.append((center_point, color))
        if len(line) == 0:
            print('!WEBPAGE! No matches found, or no images in the folder. Make sure you run the extractMiniMap.py script first')
            return
        self.save(line)

    def edit_image(self, display_image, line, color):
        """
        Edit the provided display image with the provided line points.

        Parameters:
        - display_image: Image to be edited.
        - queued_image: Queue to hold the images for display.
        - line: Line points to be drawn on the display image.

        Returns:
        - Modified image with the line drawn.
        """
        if not line:
            line.append(line[0])
        for idx, point in enumerate(line[:-1]):
            color = tuple(map(int, self.results[idx][1]))
            # print(f"Point: {point}, Next Point: {line[idx+1]}, Color: {color}")  # Debugging statement
            modified_image = cv2.line(display_image, point, line[idx+1], color, 3, cv2.LINE_AA)
        # Explicitly convert the color tuple to integers
        # color = tuple(map(int, color))
        # modified_image = cv2.polylines(display_image, drawn_line, False, color, 3, cv2.LINE_AA)
        try:
            self.queued_image.put(modified_image)
            return modified_image
        except Exception as e:
            self.queued_image.put(display_image)
            return display_image

    def save(self, line):
        """
        Save the results and the final output image.

        Parameters:
        - line: Line points to be drawn on the final image.
        """
        save_array_data = []
        save_array_frame = []
        for i in range(len(self.results)):
            save_array_data.append((self.results[i][0][0], self.results[i][0][1]))
            save_array_frame.append(self.resultImageNumber[i])
        self.apex_utils.save(save_array_data, save_array_frame, ['Frame', 'Coords'], 'miniMapPlotter')

        final_output_base = self.game_map_image
        for idx, point in enumerate(line[:-1]):
            color = tuple(map(int, self.results[idx][1]))
            # print(f"Point: {point}, Next Point: {line[idx+1]}, Color: {color}")  # Debugging statement
            cv2.line(final_output_base, point, line[idx+1], color, 3, cv2.LINE_AA)
        final_output_base = cv2.cvtColor(final_output_base, cv2.COLOR_BGR2RGB)
        plt.imsave('outputData/FINAL.jpg', final_output_base)

    def load_map_key_points(self, keypoint_path):
        """
        Load baked key points from the given path.

        Parameters:
        - keypoint_path: Path to the key points file.

        """
        class mock_keypoints:
            pt: cv2.typing.Point2f

            def __init__(self, x, y):
                self.pt = (x, y)
        try:
            print("Loading key points")
            mapKeyPoints = np.load(keypoint_path).astype('float32')
            print("Splitting key points")
            tempKeyPoints = mapKeyPoints[:, :2]
            print("Loading descriptors")
            descriptors = np.array(mapKeyPoints[:, 7:])
            print("Converting key points")
            temp_kp = []
            for x, y in list(tempKeyPoints):
                kp = mock_keypoints(x, y)
                temp_kp.append(kp)
            print("Loading key points complete!")
            self.mapKeyPoints = {'keyPoints': temp_kp, 'descriptors': descriptors}
        except Exception as e:
            print(f"!WEBPAGE!Error loading key points: {e}")
            raise e

    def check_if_match(self, image):
        """
        Check if the provided image matches with the stored map key points.

        Parameters:
        - image: Image to be matched.

        Returns:
        - kp1, good_matches if a match is found, otherwise (False, False).
        """
        try:
            descriptors = self.mapKeyPoints['descriptors']
            kp1, des1 = self.featureMappingAlgMiniMap.detectAndCompute(image, None)
            matches = self.featureMatcher.knnMatch(des1, descriptors, k=2)

            good_matches = [m for m, n in matches if m.distance < 0.65*n.distance]

            if len(good_matches) >= self.min_match_count:
                return (kp1, good_matches)
            else:
                return (False, False)
        except Exception as e:
            print(f"!WEBPAGE!Error matching image: {e}")
            return (False, False)

    def compute_homography(self, image, kp1, good_matches):
        """
        Compute the homography for the provided image and matches.

        Parameters:
        - image: Image for which homography is to be computed.
        - kp1: Key points from the image.
        - good_matches: Good matches between the image and map key points.

        Returns:
        - ceterPoint, rectanglePoints if successful, otherwise (False, False).
        """
        try:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([self.mapKeyPoints['keyPoints']
                                  [m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if M is None:
                return (False, False)

            h, w, _ = image.shape
            pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
            rectangle_points = cv2.perspectiveTransform(pts, M)
            center_point = cv2.perspectiveTransform(np.float32((115, 86)).reshape(-1, 1, 2), M)
            center_point = (int(center_point[0][0][0]), int(center_point[0][0][1]))
            return center_point, rectangle_points
        except Exception as e:
            print(f"!WEBPAGE!Error computing homography: {e}")
            return (False, False)

    def validate_match(self, rectangle_points):
        """
        Validate if the provided rectangle_points form a valid match.

        Parameters:
        - rectangle_points: Points forming the rectangle.

        Returns:
        - True if the match is valid, otherwise False.
        """
        try:
            poly_size = np.int_(cv2.contourArea(rectangle_points))
            rolling_avg = np.int_((np.sum(self.polysizeArray[-5:-1])/4))

            if poly_size != 0:
                self.polysizeArray.append(poly_size)

            if poly_size > np.int_(rolling_avg + rolling_avg * self.poly_tolerance) or poly_size < np.int_(rolling_avg - rolling_avg * self.poly_tolerance):
                self.polysizeArray.pop()
                return False
            else:
                return True
        except Exception as e:
            print(f"!WEBPAGE!Error validating match: {e}")
            return False

    def process_image(self, image_path):
        """
        Process the provided image against the game map.

        Parameters:
        - image_path: Path to the image to be processed.

        Returns:
        - center_point if the match is valid, otherwise False.
        """
        try:
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            kp1, good_matches = self.check_if_match(image)

            if kp1 is not False:
                center_point, rectangle_points = self.compute_homography(image, kp1, good_matches)
                if self.validate_match(rectangle_points):
                    return center_point
                return False
            else:
                return False
        except Exception as e:
            print(f"!WEBPAGE!Error processing image: {e}")
            return False

    def start_in_thread(self, options):
        if self.running_thread and self.running_thread.is_alive():
            print("!WEBPAGE! Minimap plotter is already running")
            return
        self.stop_event.clear()
        self.running_thread = threading.Thread(target=self.main, args=(options,), daemon=True)
        self.running_thread.start()

    def check_stop(self):
        if self.stop_event.is_set():
            print("!WEBPAGE! Stopping Minimap plotter")
            return True
        return False

    def stop(self):
        self.stop_event.set()
        self.end.value = 1

    def main(self, options):
        """
        Main execution function for the MiniMapPlotter.
        """
        # if not self.map_name or not self.game_image_ratio:
        #     raise ValueError('Map or ratio not set')
        print('!WEBPAGE! Starting MiniMap Plotter')
        self.map_name = options['map']
        self.game_image_ratio = options['ratio']
        # try:
        #     self.min_match_count = int(options['min_match_count'])
        # except Exception as e:
        #     pass
        # try:
        #     self.poly_tolerance = float(options['poly_tolerance'])
        # except Exception as e:
        #     pass
        # try:
        #     self.start_color = tuple(map(int, options['start_color'].split(',')))
        # except Exception as e:
        #     pass
        # try:
        #     self.end_color = tuple(map(int, options['end_color'].split(',')))
        # except Exception as e:
        #     pass

        self.end = multiprocessing.Value('i', 0)
        self.queued_image = multiprocessing.Queue()
        self.setup_map()
        self.apex_utils.display(self.queued_image, self.end, 'minimap-plotter')
        self.process_all_images()
        print('!WEBPAGE! Finished MiniMap Plotter')


if __name__ == '__main__':
    miniMapMatching = MiniMapPlotter('BM', '4by3')
    miniMapMatching.main()
