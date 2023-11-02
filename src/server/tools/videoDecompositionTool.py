import threading
import time
import ffmpeg
import glob
import os
from src.util.apexUtils import ApexUtils as util


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
        # for file in glob.glob("video/" + '/*.mp4'):
        for file in glob.glob("video/" + '/*.mkv'):
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
                "miniMap": "crop=237:179:52:38,hqdn3d,select=eq(pict_type\,I)",
                "PlayerDamage": "crop=45:14:1785:74,hqdn3d,select=eq(pict_type\,I)",
                "PlayerGuns": "crop=337:24:1509:1040,hqdn3d,select=eq(pict_type\,I)",
                "PlayerHealth": "crop=244:12:176:1025,hqdn3d,select=eq(pict_type\,I)",
                "PlayerKills": "crop=45:14:1635:74,hqdn3d,select=eq(pict_type\,I)",
                "PlayerShield": "crop=234:8:176:1017,hqdn3d,select=eq(pict_type\,I)",
                "PlayerTac": "crop=70:29:582:1043,hqdn3d,select=eq(pict_type\,I)",
                "PlayerUlt": "crop=45:19:938:1046,hqdn3d,select=eq(pict_type\,I)",
                "Teammate1Health": "crop=160:8:139:932,hqdn3d,select=eq(pict_type\,I)",
                "Teammate1Shield": "crop=160:7:139:926,hqdn3d,select=eq(pict_type\,I)",
                "Teammate2Health": "crop=160:8:139:882,hqdn3d,select=eq(pict_type\,I)",
                "Teammate2Shield": "crop=164:8:139:876,hqdn3d,select=eq(pict_type\,I)",
                "ZoneTimer": "crop=240:65:50:219,hqdn3d,select=eq(pict_type\,I)",
                "killFeed": "crop=433:100:1387:155,hqdn3d,select=eq(pict_type\,I)",
                "PlayerEvo": "crop=35:19:347:965,hqdn3d,select=eq(pict_type\,I)",
                "frames": "hqdn3d,select=eq(pict_type\,I)"
            }

        else:
            stream = ffmpeg.input("video/"+fileName, skip_frame='nokey', vsync=0, hwaccel='cuda')
            filter_chains = {
                "miniMap": "crop=237:179:52:38",
                "PlayerDamage": "crop=45:14:1785:74",
                "PlayerGuns": "crop=337:24:1509:1040",
                "PlayerHealth": "crop=244:12:176:1025",
                "PlayerKills": "crop=45:14:1635:74",
                "PlayerShield": "crop=234:8:176:1017",
                "PlayerTac": "crop=70:29:582:1043",
                "PlayerUlt": "crop=45:19:938:1046",
                "Teammate1Health": "crop=160:8:139:932",
                "Teammate1Shield": "crop=160:7:139:926",
                "Teammate2Health": "crop=160:8:139:882",
                "Teammate2Shield": "crop=164:8:139:876",
                "ZoneTimer": "crop=240:65:50:219",
                "killFeed": "crop=433:100:1387:155",
                "PlayerEvo": "crop=35:19:347:965",
                "frames": "null"
            }

        for output_name, filter_chain in filter_chains.items():
            if self.check_stop():
                return
            # only extract the frames on the selected output folders
            if to_extract is not None:
                if output_name not in to_extract:
                    continue
            print("!WEBPAGE! Running extraction on: " + output_name)
            output_path = os.path.join(basepath, output_name, f"{output_name}%04d.png")
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

        print("!WEBPAGE! Finished extracting frames")

    def start_in_thread(self, options):
        if self.running_thread and self.running_thread.is_alive():
            print("!WEBPAGE! A decomposition is already running")
            return
        self.stop_event.clear()
        self.running_thread = threading.Thread(target=self.decompose_video, args=(options,))
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
