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

        killFeed = ffmpeg.output(ffmpeg.crop(stream, 1387, 155, 433, 100), outputKillFeed + 'killFeed%04d.png')
        ffmpeg.run_async(killFeed)

        PlayerEvo = ffmpeg.output(ffmpeg.crop(stream, 347, 965, 35, 19), outputPlayerEvo + 'PlayerEvo%04d.png')
        ffmpeg.run_async(PlayerEvo)

        miniMap = ffmpeg.output(ffmpeg.crop(stream, 49, 37, 241, 181), outputMiniMap + 'miniMap%04d.png')
        ffmpeg.run_async(miniMap)

        PlayerDamage = ffmpeg.output(ffmpeg.crop(stream, 1785, 74, 45, 14), outputPlayerDamage + 'PlayerDamage%04d.png')
        ffmpeg.run_async(PlayerDamage)

        PlayerGuns = ffmpeg.output(ffmpeg.crop(stream, 1509, 1040, 337, 24), outputPlayerGuns + 'PlayerGuns%04d.png')
        ffmpeg.run_async(PlayerGuns)

        PlayerHealth = ffmpeg.output(ffmpeg.crop(stream, 176, 1025, 244, 12),
                                     outputPlayerHealth + 'PlayerHealth%04d.png')
        ffmpeg.run_async(PlayerHealth)

        PlayerKills = ffmpeg.output(ffmpeg.crop(stream, 1635, 74, 45, 14), outputPlayerKills + 'PlayerKills%04d.png')
        ffmpeg.run_async(PlayerKills)

        PlayerShield = ffmpeg.output(ffmpeg.crop(stream, 176, 1017, 234, 8),
                                     outputKPlayerShield + 'PlayerShield%04d.png')
        ffmpeg.run_async(PlayerShield)

        PlayerTac = ffmpeg.output(ffmpeg.crop(stream, 582, 1043, 70, 29), outputPlayerTac + 'PlayerTac%04d.png')
        ffmpeg.run_async(PlayerTac)

        PlayerUlt = ffmpeg.output(ffmpeg.crop(stream, 938, 1046, 45, 19), outputPlayerUlt + 'PlayerUlt%04d.png')
        ffmpeg.run_async(PlayerUlt)

        Teammate1Health = ffmpeg.output(ffmpeg.crop(stream, 139, 932, 160, 8),
                                        outputTeammate1Health + 'Teammate1Health%04d.png')
        ffmpeg.run_async(Teammate1Health)

        Teammate1Shield = ffmpeg.output(ffmpeg.crop(stream, 139, 926, 160, 7),
                                        outputTeammate1Shield + 'Teammate1Shield%04d.png')
        ffmpeg.run_async(Teammate1Shield)

        Teammate2Health = ffmpeg.output(ffmpeg.crop(stream, 139, 882, 160, 8),
                                        outputTeammate2Health + 'Teammate2Health%04d.png')
        ffmpeg.run_async(Teammate2Health)

        Teammate2Shield = ffmpeg.output(ffmpeg.crop(stream, 139, 876, 164, 8),
                                        outputTeammate2Shield + 'Teammate2Shield%04d.png')
        ffmpeg.run_async(Teammate2Shield)

        ZoneTimer = ffmpeg.output(ffmpeg.crop(stream, 50, 219, 240, 65), outputZoneTimer + 'ZoneTimer%04d.png')
        ffmpeg.run_async(ZoneTimer)

        frames = ffmpeg.output(stream, frames + 'frame%04d.png')
        ffmpeg.run_async(frames)

        print('Video Decomposition Tool Finished')


if __name__ == '__main__':
    videoDecompositionTool = VideoDecompositionTool()
    videoDecompositionTool.decompose_video()
