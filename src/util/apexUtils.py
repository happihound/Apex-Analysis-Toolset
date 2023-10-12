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
from PIL import Image, ImageDraw, ImageFont


class ApexUtils:

    def __init__(self):
        self._reader = None
        self._mdodel = None

    @property
    def super_res_model(self):
        """Lazy loading of OpenCV's DNN super resolution model"""
        if self._model is None:
            self._model = cv2.dnn_superres.DnnSuperResImpl_create()
            self._model.readModel('src/internal/super_resolution/EDSR_x4.pb')
            self._model.setModel("edsr", 4)
        return self._model

    @property
    def reader(self):
        """Lazy loading of easyocr.Reader"""
        if self._reader is None:
            self._reader = easyocr.Reader(['en'])
        return self._reader

    def extract_numbers_from_image(self, image):
        image = self.super_res_model.upsample(image)
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
        image = self.super_res_model.upsample(image)
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

    @staticmethod
    def combineAllCSVs():
        # Path to the folder containing the CSV files
        folder_path = 'outputdata/'
        master_dict = {}
        all_headers = set()  # To accumulate all unique filenames

        # Iterate through each CSV file in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                print(f"Processing: {filename}")  # Print the filename being processed
                with open(os.path.join(folder_path, filename), 'r') as file:
                    reader = csv.reader(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    next(reader, None)  # Skip header row if it exists
                    for row in reader:
                        try:
                            frame_num = int(row[0])
                            value = row[1]
                            if frame_num not in master_dict:
                                master_dict[frame_num] = {}

                            # Special handling for Player Guns.csv
                            if filename == "Player Guns.csv":
                                gun_key = filename
                                counter = 1
                                while gun_key in master_dict[frame_num]:
                                    counter += 1
                                    gun_key = f"{filename} Gun{counter}"
                                master_dict[frame_num][gun_key] = value
                                all_headers.add(gun_key)
                            else:
                                master_dict[frame_num][filename] = value
                                all_headers.add(filename)
                        except ValueError:
                            print(f"Skipped row in {filename}: {row}")  # Print skipped rows
                            continue

        # Convert the set of headers to a sorted list and insert 'Frame' at the beginning
        headers = sorted(list(all_headers))
        headers.insert(0, "Frame")
        print(f"Headers: {headers}")

        # Write the master dictionary to a new CSV file
        with open('merged.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for frame_num, data in sorted(master_dict.items()):
                row = [frame_num] + [data.get(header, "null") for header in headers[1:]]
                writer.writerow(row)

    @staticmethod
    def wrap_text(text, draw, font, max_width):
        """Wrap text to fit within specified width."""
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and draw.textlength(line + words[0], font=font) <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line)
        return lines

    @staticmethod
    def visualize():
        csv_path = 'merged.csv'
        frames_dir = 'src/internal/input/frames'
        output_dir = 'outputData/frames'

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # delete all files in the output directory
        for file in glob.glob(output_dir + '/*.png'):
            os.remove(file)

        # Open the merged CSV file
        with open(csv_path, 'r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Get the headers
            next(reader)
            for row in reader:
                frame_num = int(row[0])
                frame_image_path = f"{frames_dir}/frame{frame_num:04}.png"

                # Open the frame image
                with Image.open(frame_image_path) as img:
                    # Create a new image with extra space on the right for the data
                    new_img = Image.new('RGB', (img.width + 300, img.height), color='black')
                    new_img.paste(img, (0, 0))

                    draw = ImageDraw.Draw(new_img)
                    font = ImageFont.truetype("arial.ttf", 25)

                    y_offset = 10  # Starting Y-offset for text
                    for i, header in enumerate(headers):
                        # remove the '.csv'
                        header = header.replace('.csv', '')
                        text = f"{header}: {row[i]}"
                        wrapped_text = ApexUtils().wrap_text(text, draw, font, 290)  # Wrap text within 290 pixels
                        for line in wrapped_text:
                            draw.text((img.width + 10, y_offset), line, font=font, fill="white")
                            y_offset += 30  # Increment Y-offset for next line

                    # Save the new image to the output directory
                    output_image_path = f"{output_dir}/frame{frame_num:04}_data.png"
                    new_img.save(output_image_path)
