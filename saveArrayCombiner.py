import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import time
from statsmodels.nonparametric.smoothers_lowess import lowess


def combine():
    data1 = loadData('temp1/temp/miniMapData(OLD).npy')
    data2 = loadData('temp1/temp/miniMapData.npy')
    x = np.concatenate((data1[0],data2[0]))
    y = np.concatenate((data1[1],data2[1]))
    z = np.concatenate((data1[2],data2[2]))
    print(x,len(x))
    print(y,len(y))
    print(z,len(z))
    save(x,y,z)
    
def save(x,y,z):
    np.save('outputdata/miniMapDataCOMBINED.npy', np.vstack((x,y, z)))
    print('Save successful')    
    
    
    
    
    
def loadData(pathToData):
    a =  np.asarray(np.load(pathToData))
    return a


if __name__ == "__main__":
    print('Starting combiner')
    queuedImage = multiprocessing.Queue()
    process1 = multiprocessing.Process(target=combine, args=())
    process1.start()