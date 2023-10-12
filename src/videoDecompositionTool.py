import ffmpeg
import glob
import os
from util.apexUtils import ApexUtils as util


class VideoDecompositionTool:
    def decompose_video(self):
        print('Starting Video Decomposition Tool')

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

        # delete all files in the output folders
        for file in glob.glob(outputKillFeed + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputPlayerEvo + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputPlayerDamage + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputMiniMap + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputPlayerGuns + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputPlayerHealth + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputPlayerKills + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputKPlayerShield + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputPlayerTac + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputPlayerUlt + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputTeammate1Health + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputTeammate1Shield + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputTeammate2Health + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputTeammate2Shield + '/*.png'):
            os.remove(file)
        for file in glob.glob(outputZoneTimer + '/*.png'):
            os.remove(file)
        for file in glob.glob(frames + '/*.png'):
            os.remove(file)
        # run the cropping procedure on all parts simultaneously
        filter_chains = {
            "miniMap": "crop=241:181:49:37,hqdn3d,select=eq(pict_type\,I)",
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
            "PlayerEvo": "crop=35:19:347:965,hqdn3d,select=eq(pict_type\,I)"
        }
        for output_name, filter_chain in filter_chains.items():
            output_path = os.path.join(basepath, output_name, f"{output_name}%04d.png")
            ffmpeg.run_async(ffmpeg.output(stream, output_path, vf=filter_chain))

        filter_chain_frames = "hqdn3d,select=eq(pict_type\,I)"
        frames = ffmpeg.output(stream, frames + 'frame%04d.png', vf=filter_chain_frames)
        ffmpeg.run_async(frames)

        print('Video Decomposition Tool Finished')


if __name__ == '__main__':
    videoDecompositionTool = VideoDecompositionTool()
    videoDecompositionTool.decompose_video()
