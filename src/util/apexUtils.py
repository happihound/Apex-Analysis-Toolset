import csv
import multiprocessing
import os
import cv2
import time
import easyocr
import glob
import numpy as np
from typing import List, Tuple, Union
import easyocr
from statsmodels.nonparametric.smoothers_lowess import lowess


class ApexUtils:

    def __init__(self):
        self._reader = None

    @property
    def reader(self):
        """Lazy loading of easyocr.Reader"""
        if self._reader is None:
            self._reader = easyocr.Reader(['en'])
        return self._reader

    def extract_numbers_from_image(self, image):
        result_OCR = self.reader.readtext(image, allowlist='0123456789', paragraph=False)
        return result_OCR

    @staticmethod
    def load_files_from_directory(directory: str, extension: str = '*.png') -> List[str]:
        files = glob.glob(os.path.join(directory, extension))
        if not files:
            exception = FileNotFoundError(f'No images found in {directory}')
            print(exception)
            raise exception
        return files

    @staticmethod
    def extract_frame_number(file_name: str) -> int:
        return int(os.path.splitext(os.path.basename(file_name))[0][-4:])

    @staticmethod
    def get_path_to_images() -> str:
        return 'src/internal/input/'

    def display(self, queued_image: multiprocessing.Queue, end: multiprocessing.Value, window_name: str):
        '''Displays images from a queue
        queued_image: queue of images to be displayed
        end: multiprocessing.Value that is set to 1 when the program is to end
        window_name: name of the window to be displayed
        '''
        display_process = multiprocessing.Process(
            target=self.run_display, args=(queued_image, end, window_name))
        display_process.start()
        return display_process

    def run_display(self, queued_image: multiprocessing.Queue, end: multiprocessing.Value, window_name: str):
        cv2.namedWindow(window_name)
        cv2.imshow(window_name, cv2.imread('src/internal/default.png'))
        while not end.value:
            if not queued_image.empty():
                cv2.imshow(window_name, queued_image.get())
            cv2.waitKey(1)

    def extract_text_from_image(self, image):
        result_OCR = self.reader.readtext(image, paragraph=False)
        return result_OCR

    @staticmethod
    def save(data: List[int], frame: List[int], headers: List[str] = None, name: str = 'default', debug: bool = False):
        '''Saves data as a csv file
        data: list of data to be saved
        frame: frame number of the data
        headers: list of headers for the data
        name: name of the file to be saved
        '''
        lowess_frac = 0.002  # size of data (%) for estimation =~ smoothing window
        lowess_it = 0
        lowess_delta = 2
        if type(data[0]) == int:
            data = lowess(data, frame, is_sorted=False, frac=lowess_frac,
                          it=lowess_it, delta=lowess_delta, return_sorted=False)
        if data is None or frame is None:
            print("No data to save!")
            raise Exception
        try:
            if not name:
                print("No name given, trying to save as default.csv")
                name = 'default'
            if debug:
                name = f"test_{name}"
        except FileExistsError:
            pass
        try:
            with open(f'outputdata/{name}.csv', 'x', newline='') as file:
                if headers is None:
                    headers = ['Frame', 'Data']
                writer = csv.writer(file)
                writer.writerow(headers)
                for i in range(len(data)):
                    writer.writerow([frame[i], data[i]])
                print(f"Saved as {name}.csv")
        except FileExistsError:
            print(f"{name}.csv already exists, it will be overwritten!")
            # confirm = input("Are you sure you want to continue? (y/n): ")
            confirm = 'y'
            if confirm == 'y':
                # delete the file to make space for the new one
                os.remove(f'outputdata/{name}.csv')
                with open(f'outputdata/{name}.csv', 'w', newline='') as file:
                    if headers is None:
                        headers = ['Frame', 'Data']
                    writer = csv.writer(file)
                    writer.writerow(headers)
                    for i in range(len(data)):
                        writer.writerow([frame[i], data[i]])
                    print(f"Saved as {name}.csv")
            else:
                print("Save cancelled")
                return
        except Exception as e:
            print(f"Error: {e}")
            return
