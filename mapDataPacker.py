import numpy as np
import cv2 as cv
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import threading
import math
import os
import sys
editedImage = cv2.imread('maps/mapWE4by3.png')
featureMappingAlg= cv.SIFT_create(nOctaveLayers=25,nfeatures=250000)
kp1, des1 = featureMappingAlg.detectAndCompute(editedImage,None)
kpts = np.array([[kp.pt[0], kp.pt[1], kp.size,
                  kp.angle, kp.response, kp.octave,
                  kp.class_id]
                 for kp in kp1])

desc = np.array(des1)
print(str(len(kp1)))
plt.imsave('we4by3Verbose.png',cv2.cvtColor(cv2.drawKeypoints(editedImage,kp1,editedImage,flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS),cv2.COLOR_BGR2RGB))

np.save('we4by3KeyPoints.npy', np.hstack((kpts,desc)))
    
    