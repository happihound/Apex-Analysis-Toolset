import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import time
from statsmodels.nonparametric.smoothers_lowess import lowess
from util.apexUtils import ApexUtils as util

def healthFinder(pathToImages, queuedImage):
    matchCount = 0
    loopNumber = 0
    imageCount = 0
    all_Images = []
    time = []
    data = []
    for file in glob.glob(pathToImages + '/*.png'):
        all_Images.append(cv2.imread(file))
        imageCount = imageCount+1
    print('Number of images to match ' + str(imageCount))
    for file in glob.glob(pathToImages + '/*.png'):
        print('PICTURE NUMBER ' + str(loopNumber))
        image = all_Images[loopNumber]
        shield = parse_hp(image, queuedImage)
        shield = int(shield * 1.25)
        if shield:
            print(shield)
            if shield > 120:
                shield = 125
            if shield < 5:
                shield = 0
            matchCount = matchCount + 1
            data.append(shield)
            time.append(loopNumber)

        loopNumber = loopNumber+1
    time.append(imageCount)
    save(data, time)
    graph(data, time)


def parse_hp(hp_area, queuedImage):
    width = int(hp_area.shape[1] * 5)
    height = int(hp_area.shape[0] * 5)
    dim = (width, height)

    # resize image
    resized = cv2.resize(hp_area, dim, interpolation=cv2.INTER_AREA)
    # Color segmentation
    hsv = cv2.cvtColor(resized, cv2.COLOR_RGB2HSV)
    lower_red = np.array([0, 0, 220])
    upper_red = np.array([220, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(resized, resized, mask=mask)
    # Contour exctraction
    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    blurred = cv2.blur(imgray, (25, 75))
    blurred = cv2.blur(blurred, (35, 80))
    blurred = cv2.medianBlur(blurred, 151)

    _, thresholded = cv2.threshold(blurred, 50, 255, 0)
    queuedImage.put(thresholded)
    time.sleep(0.05)
    contours, _ = cv2.findContours(thresholded, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)
    if contours:
        cnt = contours[0]
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        if cv2.contourArea(cnt) > 600:  # to discard noise from the color segmentation
            contour_poly = cv2.approxPolyDP(cnt, 30, True)
            center, radius = cv2.minEnclosingCircle(contour_poly)
            if int(center[0]) <= width/2:
                cv2.circle(resized, (int(center[0]), int(center[1])), int(radius), (0, 255, 0), 2)
                # queuedImage.put(resized)
                resized_width = int(resized.shape[1])
                hp_width = radius * 2

                return int(hp_width * 106 / resized_width)
    return -1


def graph(foundData, loopNumber):
    x, y = (smoothing(foundData, loopNumber))
    plt.plot(x, y)
    plt.xlabel("Time")
    plt.ylabel("Shield")
    plt.show()
    plt.pause(100)


def save(foundData, imageNumber):
    np.save('outputdata/playerShieldData.npy', np.vstack((foundData, imageNumber)))


def smoothing(y, x):
    y = filterValues(y)
    lowess_frac = 0.05  # size of data (%) for estimation =~ smoothing window
    lowess_it = 0
    lowess_delta = 2
    x_smooth = x
    y_smooth = lowess(y, x, is_sorted=False, frac=lowess_frac, it=lowess_it, delta=lowess_delta, return_sorted=False)
    return x_smooth, y_smooth


def filterValues(values):
    loopNumber = 2
    newValues = values.copy()
    for i in values:
        loopNumber = loopNumber + 1
        if loopNumber > len(values)-2:
            break

        if values[loopNumber-1] == values[loopNumber+1]:
            newValues[loopNumber] = values[loopNumber-1]
    return newValues


if __name__ == "__main__":
    print('Starting player shield tracker')
    queuedImage = multiprocessing.Queue()
    pathToImages = 'inputData/playerShield/'
    end = multiprocessing.Value("i", False)
    process1 = multiprocessing.Process(target=healthFinder, args=(pathToImages, queuedImage, end))
    process2 = multiprocessing.Process(target=(util.display), args=(queuedImage, end, 'Health'))
    process1.start()
    process2.start()
