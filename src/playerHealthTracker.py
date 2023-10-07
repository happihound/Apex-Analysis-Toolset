import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import time
from tqdm import tqdm
from util.apexUtils import ApexUtils as util
from statsmodels.nonparametric.smoothers_lowess import lowess


def healthFinder(pathToImages, queuedImage):
    matchCount = 0
    loopNumber = 0
    imageCount = 0
    all_Images = []
    imageNumber = []
    foundData = []
    for file in glob.glob(pathToImages + '/*.png'):
        all_Images.append(cv2.imread(file))
        imageCount = imageCount + 1
    print('Number of images to match ' + str(imageCount))
    for _ in tqdm(glob.glob(pathToImages + '/*.png')):
        print('PICTURE NUMBER ' + str(loopNumber))
        image = all_Images[loopNumber]
        # Check health
        health = parse_hp(image, queuedImage)
        if health:
            if health > -1:
                if health > 99:
                    health = 100
                if health < 3:
                    health = 0
                print(health)
                matchCount = matchCount + 1
                foundData.append(health)
                imageNumber.append(loopNumber)
        loopNumber = loopNumber + 1
    save(foundData, imageNumber)
    graph(foundData, imageNumber)


def display(queuedImage):
    cv2.namedWindow('health')
    cv2.imshow("health", cv2.imread('inputData/default.png'))
    while True:
        if not queuedImage.empty():
            cv2.imshow("health", queuedImage.get())
            continue
        cv2.waitKey(1)


def parse_hp(hp_area, queuedImage):
    width = int(hp_area.shape[1] * 5)
    height = int(hp_area.shape[0] * 5)
    dim = (width, height)

    # resize image
    resized = cv2.resize(hp_area, dim, interpolation=cv2.INTER_AREA)
    # Color segmentation
    hsv = cv2.cvtColor(resized, cv2.COLOR_RGB2HSV)
    lower_red = np.array([0, 0, 220])
    upper_red = np.array([180, 45, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(resized, resized, mask=mask)
    # Contour extraction
    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(imgray, (5, 5), 0)
    # Apply light blurring
    _, thresholded = cv2.threshold(blurred, 50, 255, 0)
    contours, _ = cv2.findContours(
        thresholded, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)
    if contours:
        cnt = contours[0]
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        if cv2.contourArea(cnt) > 600:  # discard noise from the color segmentation
            contour_poly = cv2.approxPolyDP(cnt, 30, True)
            center, radius = cv2.minEnclosingCircle(contour_poly)
            if int(center[0]) <= width / 2:
                cv2.circle(resized, (int(center[0]), int(
                    center[1])), int(radius), (0, 255, 0), 2)

                resized_width = int(resized.shape[1])
                hp_width = radius * 2

                return int(hp_width * 100 / resized_width)
    # Check if user is downed
    resized1 = cv2.resize(hp_area, dim, interpolation=cv2.INTER_AREA)
    hsv1 = cv2.cvtColor(resized1, cv2.COLOR_RGB2HSV)
    lower1 = np.array([60, 200, 190])
    upper1 = np.array([160, 255, 215])
    mask1 = cv2.inRange(hsv1, lower1, upper1)
    res1 = cv2.bitwise_and(resized1, resized1, mask=mask1)
    # Contour extraction
    imgray1 = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)
    blurred1 = cv2.GaussianBlur(imgray1, (5, 5), 0)

    _, thresholded1 = cv2.threshold(blurred1, 50, 255, 0)
    contours1, _ = cv2.findContours(
        thresholded1, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)
    if contours1:
        cnt1 = contours1[0]
        queuedImage.put(thresholded1)
        if cv2.contourArea(cnt1) > 200 and cv2.contourArea(cnt1) < 160000:
            return 1
        else:
            return -1
    else:
        return -1
    return -1


def graph(foundData, loopNumber):
    x, y = (smoothing(foundData, loopNumber))
    plt.plot(x, y)
    plt.xlabel("Time")
    plt.ylabel("Health")
    plt.show()
    plt.pause(100)


def save(foundData, imageNumber):
    np.save('outputdata/playerHealthData.npy',
            np.vstack((foundData, imageNumber)))


def smoothing(y, x):
    y = filterValues(y)
    lowess_frac = 0.002  # size of data (%) for estimation =~ smoothing window
    lowess_it = 0
    lowess_delta = 2
    x_smooth = x
    y_smooth = lowess(y, x, is_sorted=False, frac=lowess_frac,
                      it=lowess_it, delta=lowess_delta, return_sorted=False)
    return x_smooth, y_smooth


def filterValues(values):
    loopNumber = 2
    newValues = values.copy()
    for i in values:
        loopNumber = loopNumber + 1
        if loopNumber > len(values) - 2:
            break

        if values[loopNumber - 1] == values[loopNumber + 1]:
            newValues[loopNumber] = values[loopNumber - 1]
    return newValues


if __name__ == "__main__":
    print('Starting player health tracker')
    queuedImage = multiprocessing.Queue()
    pathToImages = 'inputData/playerHealth/'
    process1 = multiprocessing.Process(
        target=healthFinder, args=(pathToImages, queuedImage,))
    process2 = multiprocessing.Process(target=display, args=(queuedImage,))
    process1.start()
    process2.start()
