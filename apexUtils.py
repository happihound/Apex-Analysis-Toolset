import csv
import multiprocessing
import cv2
import time


class ApexUtils:
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
        time.sleep(1)
        cv2.namedWindow(window_name)
        cv2.imshow(window_name, cv2.imread('internal/default.png'))
        while not end.value:
            if not queued_image.empty():
                cv2.imshow(window_name, queued_image.get())
            cv2.waitKey(1)

    def save(self, data, frame, headers=None, name='default', debug=False):
        '''Saves data as a csv file
        data: list of data to be saved
        frame: frame number of the data
        headers: list of headers for the data
        name: name of the file to be saved
        '''
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
            print(f"{name}.csv already exists, it will not be overwritten!")
            raise FileExistsError
        except FileNotFoundError:
            print("Save failed! Please check that the outputdata folder exists")
            raise FileNotFoundError
