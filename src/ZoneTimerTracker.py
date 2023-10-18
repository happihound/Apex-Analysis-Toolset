import numpy as np
import cv2
import multiprocessing
from tqdm import tqdm
from util.apexUtils import ApexUtils as util


class ZoneTimerTracker:

    __slots__ = ['path_to_images', 'queued_image', 'end', 'apex_utils',
                 'frame_number', 'match_count', 'results', 'result_image_number']

    def __init__(self):
        self.queued_image = None
        self.frame_number = 0
        self.match_count = 0
        self.results = [0]
        self.result_image_number = [0]
        self.apex_utils = util()
        self.path_to_images = util().get_path_to_images() + "/zoneTimer"

    def track_timer(self, queued_image, end) -> None:
        self.end = end
        self.queued_image = queued_image
        files = self.apex_utils.load_files_from_directory(self.path_to_images)

        for file in tqdm(files):
            self.frame_number = self.apex_utils.extract_frame_number(file)
            image = cv2.imread(file)
            # readtext(image, allowlist='0123456789secSEC', paragraph=False)
            result = self.apex_utils.extract_text_from_image(image)
            self.process_result(result)
            self.queued_image.put(image)

        self.results = self.filter_values(self.results)

       # print(f'found {self.match_count} total matches')
        end.value = 1
        self.graph_filter_and_save(self.result_image_number, self.results)

    def process_result(self, result) -> None:
        if len(result):
            for (bbox, text, prob) in result:
                if text == '':
                    continue
                # Remove unwanted text
                if ':' in text or '.' in text:
                    try:
                        clean_text = ''.join(ch for ch in text if ch.isdigit() or ch == '.' or ch == ':')
                        # replace all . with :
                        clean_text = clean_text.replace('.', ':')
                        # split the string into a list of strings
                        clean_text = clean_text.split(':')
                        if len(clean_text) != 2:
                            continue
                        minute = clean_text[0]
                        try:
                            if minute[0] == '0':
                                minute = minute[1]
                        except Exception as e:
                            continue
                        second = clean_text[1]
                        # print('\n')
                        # print(minute+':'+second)
                        # print('\n')
                        if second > '59':
                            continue
                        if minute > '6':
                            continue
                        text = int(minute) * 60 + int(second)
                        self.match_count += 1
                        self.results.append(text)
                        self.result_image_number.append(self.frame_number)
                    except Exception as e:
                        continue
        else:
            self.results.append(self.results[-1])
            self.result_image_number.append(self.frame_number)

    def filter_values(self, values):
        new_values = [values[0]]

        # Iterate over the values, skipping the first and last ones
        for i in range(1, len(values) - 1):
            # If the previous and next values are the same, set the current value to the previous value
            if values[i - 1] == values[i + 1]:
                new_values.append(values[i - 1])
            # Check if the value at i is over or under 10 from the previous and next values
            elif abs(values[i] - values[i - 1]) > 15 and abs(values[i] - values[i + 1]) > 15:
                # Replace the value at i with the average of the previous and next values
                new_values.append((values[i - 1] + values[i + 1]) // 2)
            else:
                new_values.append(values[i])
        new_values.append(values[-1])
        return new_values

    def graph_filter_and_save(self, frame_number, results) -> None:
        # plt.plot(x, y)
        # plt.xlabel("Time")
        # plt.ylabel("Time Till Zone Close")
        # plt.xlim([0, len(frame_number)])
        # plt.show()
        # plt.pause(99999)
        self.apex_utils.save(results, frame_number, ["Frame", "Zone Timer"], 'Zone Timer')

    def main(self) -> None:
        print('Starting zone timer tracker')
        end = multiprocessing.Value("i", False)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Zone Timer Tracker')
        self.track_timer(queued_image, end)
        print('Finished zone timer tracker')


if __name__ == '__main__':
    zone_timer_tracker = ZoneTimerTracker()
    zone_timer_tracker.main()
