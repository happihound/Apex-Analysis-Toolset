import os
import csv
import damageTracker
import evoTracker
import killFeedNameFinder
import miniMapPlotter
import playerGunTracker
import playerHealthTracker
import playerKillTracker
import playerShieldTracker
import playerTacTracker
import playerUltTracker
import videoDecompositionTool
import util.apexUtils as util
import ZoneTimerTracker
from PIL import Image, ImageDraw, ImageFont

'''
This class runs all of the other classes and
is responsible for collecting their various outputs into one large table.
'''

'''
Quick options:
do_frame_extraction=True
do_teammate_extraction=True
do_ocr_extractions=True
do_mini_map_plotter=True
methods_to_run=None - if None, all methods will be run otherwise pass a list of methods to run
'''


class Coordinator:

    __slots__ = ['run_all_methods', 'methods_to_run', 'run_frame_extraction']

    def __init__(self, methods_to_run='all', do_frame_extraction=False):
        if do_frame_extraction:
            self.run_frame_extraction = True
        else:
            self.run_frame_extraction = False
        if methods_to_run is None or type(methods_to_run) is str and methods_to_run.lower() == 'all':
            self.run_all_methods = True
            self.methods_to_run = []
        else:
            self.run_all_methods = False
            self.methods_to_run = methods_to_run

    def runTrackers(self):
        print("Running the following trackers:", end='\n')
        if self.run_all_methods:
            print("all")
        else:
            print(self.methods_to_run)
        if (self.run_all_methods or 'videoDecompositionTool' in self.methods_to_run) and self.run_frame_extraction:
            print("Running video decomposition tool", end='\n\t')
            self.runVideoDecompositionTool()
        if self.run_all_methods or 'playerKillTracker' in self.methods_to_run:
            print("Running player kill tracker", end='\n\t')
            self.runPlayerKillTracker()
        if self.run_all_methods or 'playerGunTracker' in self.methods_to_run:
            print("Running player gun tracker", end='\n\t')
            self.runPlayerGunTracker()
        if self.run_all_methods or 'playerHealthTrackerAndTeammates' in self.methods_to_run:
            print("Running player health tracker and teammates", end='\n\t')
            self.runPlayerHealthTrackerAndTeammates()
        if self.run_all_methods or 'playerShieldTrackerAndTeammates' in self.methods_to_run:
            print("Running player shield tracker and teammates", end='\n\t')
            self.runPlayerShieldTrackerAndTeammates()
        if not self.run_all_methods or 'playerHealthTracker' in self.methods_to_run:
            print("Running player health tracker", end='\n\t')
            self.runPlayerHealthTracker()
        if not self.run_all_methods or 'playerShieldTracker' in self.methods_to_run:
            print("Running player shield tracker", end='\n\t')
            self.runPlayerShieldTracker()
        if self.run_all_methods or 'playerUltTracker' in self.methods_to_run:
            print("Running player ult tracker", end='\n\t')
            self.runPlayerUltTracker()
        if self.run_all_methods or 'playerTacFinder' in self.methods_to_run:
            print("Running player tac finder", end='\n\t')
            self.runPlayerTacFinder()
        if self.run_all_methods or 'killFeedNameFinder' in self.methods_to_run:
            print("Running kill feed name finder", end='\n\t')
            self.runKillFeedNameFinder()
        if self.run_all_methods or 'evoTracker' in self.methods_to_run:
            print("Running evo tracker", end='\n\t')
            self.runEvoTracker()
        if self.run_all_methods or 'damageTracker' in self.methods_to_run:
            print("Running damage tracker", end='\n\t')
            self.runDamageTracker()
        if self.run_all_methods or 'miniMapPlotter' in self.methods_to_run:
            print("Running mini map plotter", end='\n\t')
            self.runMiniMapPlotter()
        if self.run_all_methods or 'zoneTimer' in self.methods_to_run:
            print("Running zone timer", end='\n\t')
            self.runZoneTimer()

    def runVideoDecompositionTool(self):
        videoDecompositionTool.VideoDecompositionTool().decompose_video()

    def runPlayerKillTracker(self):
        playerKillTracker.KillTracker().main()

    def runPlayerGunTracker(self):
        playerGunTracker.GunTracker().main()

    def runPlayerHealthTrackerAndTeammates(self):
        playerHealthTracker.HealthTracker('/playerHealth').main()
        playerHealthTracker.HealthTracker('/teammate1Health').main()
        # playerHealthTracker.HealthTracker('/teammate2Health').main()

    def runPlayerShieldTrackerAndTeammates(self):
        playerShieldTracker.ShieldTracker('/playerShield').main()
        playerShieldTracker.ShieldTracker('/teammate1Shield').main()
        # playerShieldTracker.ShieldTracker('/teammate2Shield').main()

    def runPlayerHealthTracker(self):
        playerHealthTracker.HealthTracker('/playerHealth').main()

    def runPlayerShieldTracker(self):
        playerShieldTracker.ShieldTracker('/playerShield').main()

    def runPlayerUltTracker(self):
        playerUltTracker.UltTracker().main()

    def runPlayerTacFinder(self):
        playerTacTracker.TacTracker().main()

    def runKillFeedNameFinder(self):
        print("skipping kill feed name finder")
        return
        # killFeedNameFinder.KillFeedNameFinder().main()

    def runEvoTracker(self):
        evoTracker.EvoTracker().main()

    def runDamageTracker(self):
        damageTracker.DamageTracker().main()

    def runMiniMapPlotter(self):
        print("skipping mini map plotter")
        return
        # miniMapPlotter.MiniMapPlotter().main()

    def runZoneTimer(self):
        ZoneTimerTracker.ZoneTimerTracker().main()

    def combineAllCSVs(self):
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

    def visualize(self):
        csv_path = 'merged.csv'

        frames_dir = 'src/internal/input/frames'

        output_dir = 'outputData/frames'

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Open the merged CSV file
        with open(csv_path, 'r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Get the headers
            next(reader)
            for row in reader:
                frame_num = int(row[0])
                frame_image_path = f"{frames_dir}/frame{frame_num:04}.png"  # Adjusted format for frames

                # Open the frame image
                with Image.open(frame_image_path) as img:
                    # Create a new image with extra space on the right for the data
                    new_img = Image.new('RGB', (img.width + 200, img.height), color='black')
                    new_img.paste(img, (0, 0))

                    draw = ImageDraw.Draw(new_img)
                    font = ImageFont.truetype("arial.ttf", 15)  # Use Arial font with size 15

                    y_offset = 10  # Starting Y-offset for text
                    for i, header in enumerate(headers):
                        text = f"{header}: {row[i]}"
                        draw.text((img.width + 10, y_offset), text, font=font, fill="white")
                        y_offset += 20  # Increment Y-offset for next line

                    # Save the new image to the output directory
                    output_image_path = f"{output_dir}/frame{frame_num:04}_data.png"
                    new_img.save(output_image_path)


if __name__ == '__main__':
    tracker = Coordinator('all', False)
    tracker.runTrackers()
    tracker.combineAllCSVs()
    tracker.visualize()
