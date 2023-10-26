import threading
import cv2
import matplotlib.pyplot as plt
import multiprocessing
from tqdm import tqdm
from util.apexUtils import ApexUtils as util


plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"

EVO_UPPER_LIMIT = 750  # max value for evo shield
EVO_LOWER_LIMIT = 0  # min value for evo shield

'''
This class is responsible for tracking the evo shield of the player,
it uses OCR to extract the ammount of damage until the next level.
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
    - Evo
This describes the frame number and the evo level up amount on that frame.
'''


class EvoTracker:
    __slots__ = ['end', 'queued_image', 'frame_number', 'match_count',
                 'results', 'result_image_number', 'reader', 'path_to_images', 'apex_utils', 'stop_event', 'running_thread', 'socketio']

    def __init__(self, socketio):
        self.queued_image = None
        self.end = None
        self.stop_event = threading.Event()
        self.running_thread = None
        self.socketio = socketio
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util(socketio=socketio)
        self.path_to_images = self.apex_utils.get_path_to_images() + "/playerEvo"

    def process_file(self, file, pbar):
        image = cv2.imread(file)
        # Extract the frame number from the filename
        self.frame_number = self.apex_utils.extract_frame_number(file)
        result_OCR = self.apex_utils.extract_numbers_from_image(image)
        if self.process_result(result_OCR, pbar):
            self.queued_image.put(image)

    def track_evo(self, queued_image, end):
        self.queued_image = queued_image
        self.end = end
        files = self.apex_utils.load_files_from_directory(self.path_to_images)
        with tqdm(files) as pbar:
            for file in pbar:
                if self.check_stop():
                    end.value = 1
                    break
                self.process_file(file, pbar)

        self.filter_values()
        print(f'!WEBPAGE! found {self.match_count} total matches')
        self.apex_utils.save(data=self.results, frame=self.result_image_number,
                             headers=["Frame", "Evo"], name='Evo')
        end.value = 1

    def process_result(self, result_OCR, pbar):
        for _, text, prob in result_OCR:
            if text == '':
                continue
            evo_found = int(text)
            if prob > 0.93 and self.is_valid_evo(evo_found):
                self.match_count += 1
                self.results.append(evo_found)
                self.result_image_number.append(self.frame_number)
                pbar.set_description(desc=str(self.match_count), refresh=True)
                return True
            else:
                self.results.append(self.results[-1])
                self.result_image_number.append(self.frame_number)
        return False

    @staticmethod
    def is_valid_evo(evo_found):
        return EVO_LOWER_LIMIT < evo_found <= EVO_UPPER_LIMIT

    def filter_values(self):
        new_values = [self.results[i-1] if self.results[i-1] == self.results[i+1] else value
                      for i, value in enumerate(self.results[1:-1])]
        self.results = [self.results[0]] + new_values + [self.results[-1]]
        self.match_count = len(self.results)

    def main(self):
        print('!WEBPAGE! Starting evo tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'evo-tracker')
        self.track_evo(queued_image, end)
        print('!WEBPAGE! Finished evo tracker')

    def start_in_thread(self) -> None:
        if self.running_thread and self.running_thread.is_alive():
            print("!WEBPAGE! Evo tracker is already running")
            return
        self.stop_event.clear()
        self.running_thread = threading.Thread(target=self.main)
        self.running_thread.start()

    def check_stop(self) -> bool:
        if self.stop_event.is_set():
            print("!WEBPAGE! Stopping evo tracker")
            return True
        return False

    def stop(self) -> None:
        self.stop_event.set()


if __name__ == '__main__':
    tracker = EvoTracker()
    tracker.main()
