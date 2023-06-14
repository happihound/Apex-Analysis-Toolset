import numpy as np
import cv2 as cv
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import threading
import math
import ffmpeg
import time
import os
import sys
inputVideoPath = 'OTHER/video/'
outputPath = 'other/bulkImages/'
loopnumber = 1
#Extract frames from every video contained in a folder 
for file in glob.glob(inputVideoPath+ '/*.mp4'):
    fileName = os.path.basename(file)                          
    stream = ffmpeg.input(inputVideoPath + fileName,skip_frame='nokey',vsync=0,hwaccel='cuda')
    killFeed = ffmpeg.output(ffmpeg.crop(stream, 1387, 204, 433, 75),outputPath +fileName +'_killFeed%04d.png')
    ffmpeg.run(killFeed)
    loopnumber = loopnumber+1