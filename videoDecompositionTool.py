import ffmpeg
import glob
import os
print('Starting Video Decomposition Tool')
# grab only keyframes to ensure frame quality and use GPU acceleration
fileName = ''
for file in glob.glob("videos/" + '/*.mp4'):
    fileName = os.path.basename(file)
stream = ffmpeg.input("videos/"+fileName, skip_frame='nokey', vsync=0, hwaccel='cuda')
# output path for all the various parts of the frames
outputKillFeed = 'inputData/killFeed/'
outputMiniMap = 'inputData/MiniMap/'
outputPlayerDamage = 'inputData/PlayerDamage/'
outputPlayerEvo = 'inputData/PlayerEvo/'
outputPlayerGuns = 'inputData/PlayerGuns/'
outputPlayerHealth = 'inputData/PlayerHealth/'
outputPlayerKills = 'inputData/PlayerKills/'
outputKPlayerShield = 'inputData/PlayerShield/'
outputPlayerTac = 'inputData/PlayerTac/'
outputPlayerUlt = 'inputData/PlayerUlt/'
outputTeammate1Health = 'inputData/Teammate1Health/'
outputTeammate1Shield = 'inputData/Teammate1Shield/'
outputTeammate2Health = 'inputData/Teammate2Health/'
outputTeammate2Shield = 'inputData/Teammate2Shield/'
outputWholeImage = 'inputData/WholeImage/'
outputZoneTimer = 'inputData/ZoneTimer/'
# run the cropping procedure on all parts simultaneously

decomp = ffmpeg.output(stream, 'OTHER/test1/' + 'image_%04d.png')
ffmpeg.run_async(decomp)
exit()

killFeed = ffmpeg.output(ffmpeg.crop(stream, 1387, 155, 433, 100), outputKillFeed + 'killFeed%04d.png')
ffmpeg.run_async(killFeed)

PlayerEvo = ffmpeg.output(ffmpeg.crop(stream, 347, 965, 35, 19), outputPlayerEvo + 'PlayerEvo%04d.png')
ffmpeg.run_async(PlayerEvo)

PlayerDamage = ffmpeg.output(ffmpeg.crop(stream, 1785, 74, 45, 16), outputPlayerDamage + 'PlayerDamage%04d.png')
ffmpeg.run_async(PlayerDamage)


miniMap = ffmpeg.output(ffmpeg.crop(stream, 49, 37, 241, 181), outputMiniMap + 'miniMap%04d.png')
ffmpeg.run_async(miniMap)

PlayerDamage = ffmpeg.output(ffmpeg.crop(stream, 1785, 74, 45, 14), outputPlayerDamage + 'PlayerDamage%04d.png')
ffmpeg.run_async(PlayerDamage)

PlayerEvo = ffmpeg.output(ffmpeg.crop(stream, 194, 957, 216, 31), outputPlayerEvo + 'PlayerEvo%04d.png')
ffmpeg.run_async(PlayerEvo)

PlayerGuns = ffmpeg.output(ffmpeg.crop(stream, 1509, 1040, 337, 24), outputPlayerGuns + 'PlayerGuns%04d.png')
ffmpeg.run_async(PlayerGuns)

PlayerHealth = ffmpeg.output(ffmpeg.crop(stream, 176, 1025, 244, 12), outputPlayerHealth + 'PlayerHealth%04d.png')
ffmpeg.run_async(PlayerHealth)

PlayerKills = ffmpeg.output(ffmpeg.crop(stream, 1635, 68, 90, 24), outputPlayerKills + 'PlayerKills%04d.png')
ffmpeg.run_async(PlayerKills)

PlayerShield = ffmpeg.output(ffmpeg.crop(stream, 176, 1017, 234, 8), outputKPlayerShield + 'PlayerShield%04d.png')
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
