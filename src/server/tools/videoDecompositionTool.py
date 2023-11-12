import threading
import time
import cv2
import ffmpeg
import glob
import os
from src.util.apexUtils import ApexUtils as util
# from super_resolution import cartoon_upsampling_4x


class VideoDecompositionTool:
    def __init__(self):
        self.stop_event = threading.Event()
        self.running_thread = None
        self.running_extractions = []

    def decompose_video(self, options):
        print('!WEBPAGE! Starting Video Decomposition Tool')
        running_extractions = []
        high_quality = options['high_quality']
        async_mode = options['async_mode']
        print(f"!WEBPAGE! high_quality: {high_quality}")
        print(f"!WEBPAGE! async_mode: {async_mode}")
        options.pop('high_quality')
        options.pop('async_mode')
        to_extract = []
        for key, value in options.items():
            if value:
                to_extract.append(key)
        # grab only keyframes to ensure frame quality and use GPU acceleration
        fileName = ''
        for file in glob.glob("video/" + '/*.mp4'):
            # for file in glob.glob("video/" + '/*.mkv'):
            fileName = os.path.basename(file)

        # add the hqdn3d filter to remove noise from the video
        stream = ffmpeg.input("video/"+fileName, vsync=0, hwaccel='cuda')

        # output path for all the various parts of the frames
        basepath = util.get_path_to_images()
        outputKillFeed = basepath + "/killFeed/"
        outputPlayerEvo = basepath + "/playerEvo/"
        outputPlayerDamage = basepath + "/playerDamage/"
        outputMiniMap = basepath + "/miniMap/"
        outputPlayerGuns = basepath + "/playerGuns/"
        outputPlayerHealth = basepath + "/playerHealth/"
        outputPlayerKills = basepath + "/playerKills/"
        outputKPlayerShield = basepath + "/playerShield/"
        outputPlayerTac = basepath + "/playerTac/"
        outputPlayerUlt = basepath + "/playerUlt/"
        outputTeammate1Health = basepath + "/teammate1Health/"
        outputTeammate1Shield = basepath + "/teammate1Shield/"
        outputTeammate2Health = basepath + "/teammate2Health/"
        outputTeammate2Shield = basepath + "/teammate2Shield/"
        outputZoneTimer = basepath + "/zoneTimer/"
        frames = basepath + "/frames/"
        # map args to the output paths
        output_paths = {
            "miniMap": outputMiniMap,
            "PlayerDamage": outputPlayerDamage,
            "PlayerGuns": outputPlayerGuns,
            "PlayerHealth": outputPlayerHealth,
            "PlayerKills": outputPlayerKills,
            "PlayerShield": outputKPlayerShield,
            "PlayerTac": outputPlayerTac,
            "PlayerUlt": outputPlayerUlt,
            "Teammate1Health": outputTeammate1Health,
            "Teammate1Shield": outputTeammate1Shield,
            "Teammate2Health": outputTeammate2Health,
            "Teammate2Shield": outputTeammate2Shield,
            "ZoneTimer": outputZoneTimer,
            "killFeed": outputKillFeed,
            "PlayerEvo": outputPlayerEvo,
            "frames": frames
        }

        # create all the output folders if they don't exist
        for output_name, output_path in output_paths.items():
            if not os.path.exists(output_path):
                os.makedirs(output_path)

        # only delete files in the selected output folders
        if to_extract is not None:
            for output_name, output_path in output_paths.items():
                if output_name not in to_extract:
                    continue
                for file in glob.glob(output_path + '/*.png'):
                    os.remove(file)
        else:
            # delete all
            for output_name, output_path in output_paths.items():
                for file in glob.glob(output_path + '/*.png'):
                    os.remove(file)

       # run the cropping procedure on all parts simultaneously
        if high_quality:
            filter_chains = {
                "miniMap": "crop=207:187:44:39,hqdn3d,select=eq(pict_type\,I)",
                "PlayerDamage": "crop=40:22:1547:73,hqdn3d,select=eq(pict_type\,I)",
                "PlayerGuns": "crop=256:20:1322:898,hqdn3d,select=eq(pict_type\,I)",
                "PlayerHealth": "crop=200:10:153:879,hqdn3d,select=eq(pict_type\,I)",
                "PlayerKills": "crop=29:22:1425:73,hqdn3d,select=eq(pict_type\,I)",
                "PlayerShield": "crop=201:6:153:871,hqdn3d,select=eq(pict_type\,I)",
                "PlayerTac": "crop=53:17:515:902,hqdn3d,select=eq(pict_type\,I)",
                "PlayerUlt": "crop=33:18:814:902,hqdn3d,select=eq(pict_type\,I)",
                "Teammate1Health": "crop=139:7:120:782,hqdn3d,select=eq(pict_type\,I)",
                "Teammate1Shield": "crop=136:6:120:777,hqdn3d,select=eq(pict_type\,I)",
                "Teammate2Health": "crop=139:7:120:731,hqdn3d,select=eq(pict_type\,I)",
                "Teammate2Shield": "crop=136:6:120:726,hqdn3d,select=eq(pict_type\,I)",
                "ZoneTimer": "crop=94:30:126:243,hqdn3d,select=eq(pict_type\,I)",
                "killFeed": "crop=433:100:1387:155,hqdn3d,select=eq(pict_type\,I)",
                "PlayerEvo": "crop=30:14:302:819,hqdn3d,select=eq(pict_type\,I)",
                "frames": "hqdn3d,select=eq(pict_type\,I)"
            }

        else:
            stream = ffmpeg.input(
                "video/"+fileName, skip_frame='nokey', vsync=0, hwaccel='cuda')
            filter_chains = {
                "miniMap": "crop=207:187:44:39",
                "PlayerDamage": "crop=40:22:1547:73",
                "PlayerGuns": "crop=256:20:1322:898",
                "PlayerHealth": "crop=200:10:153:879",
                "PlayerKills": "crop=29:22:1425:73",
                "PlayerShield": "crop=201:6:153:871",
                "PlayerTac": "crop=53:17:515:902",
                "PlayerUlt": "crop=33:18:814:902",
                "Teammate1Health": "crop=139:7:120:782",
                "Teammate1Shield": "crop=136:6:120:777",
                "Teammate2Health": "crop=139:7:120:731",
                "Teammate2Shield": "crop=136:6:120:726",
                "ZoneTimer": "crop=94:30:126:243",
                "killFeed": "crop=433:100:1387:155",
                "PlayerEvo": "crop=30:14:302:819",
                "frames": "null"
            }

        for output_name, filter_chain in filter_chains.items():
            # only extract the frames on the selected output folders
            if to_extract is not None:
                if output_name not in to_extract:
                    continue
            print("!WEBPAGE! Running extraction on: " + output_name)
            output_path = os.path.join(
                basepath, output_name, f"{output_name}%04d.png")
            if async_mode:
                process = ffmpeg.run_async(ffmpeg.output(
                    stream, output_path, vf=filter_chain), quiet=False, pipe_stdin=True)
                self.running_extractions.append(process)
            else:
                process = ffmpeg.run_async(ffmpeg.output(
                    stream, output_path, vf=filter_chain), quiet=False, pipe_stdin=True)
                while process.poll() is None:
                    if self.check_stop():
                        return
                    time.sleep(0.1)
        if async_mode:
            print("!WEBPAGE! Waiting for all extractions to finish")
            while len(self.running_extractions) > 0:
                if self.check_stop():
                    return
                for process in self.running_extractions:
                    if process.poll() is not None:
                        self.running_extractions.remove(process)

                time.sleep(0.1)
        # if high_quality:
        #     print("!WEBPAGE! Starting upscaling")
        #     for output_name, output_path in output_paths.items():
        #         if output_name not in to_extract:
        #             continue
        #         if output_name == "frames":
        #             continue
        #         print("!WEBPAGE! Upscaling: " + output_name)
        #         for file in glob.glob(output_path + '/*.png'):
        #             image = cartoon_upsampling_4x(file)
        #             cv2.imwrite(file, image)

        print("!WEBPAGE! Finished extracting frames")

    def start_in_thread(self, options):
        if self.running_thread and self.running_thread.is_alive():
            print("!WEBPAGE! A decomposition is already running")
            return
        self.stop_event.clear()
        self.running_thread = threading.Thread(
            target=self.decompose_video, args=(options,))
        self.running_thread.start()

    def check_stop(self):
        if self.stop_event.is_set():
            print("!WEBPAGE! Stopping video decomposition tool")
            self.kill()
            return True
        return False

    def kill(self):
        for process in self.running_extractions:
            process.communicate(str.encode("q"))
            process.terminate()

    def stop(self):
        self.stop_event.set()


if __name__ == '__main__':
    videoDecompositionTool = VideoDecompositionTool()
    videoDecompositionTool.decompose_video()
