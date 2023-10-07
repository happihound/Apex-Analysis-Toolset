import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import easyocr
from statsmodels.nonparametric.smoothers_lowess import lowess
import jellyfish
from tqdm import tqdm

plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"


def playerTacTracker(pathToImages, queuedImage):
    matchCount = 0
    loopNumber = 0
    imageCount = 0
    foundData = []
    imageNumber = []
    all_Images = []
    foundData.append(0)
    imageNumber.append(0)
    for file in glob.glob(pathToImages + '/*.png'):
        all_Images.append(cv2.imread(file))
        imageCount = imageCount+1
    print('Number of images to match ' + str(imageCount))
    reader = easyocr.Reader(['en'])
    for file in tqdm(glob.glob(pathToImages + '/*.png')):
        loopNumber = loopNumber + 1
        image = all_Images[loopNumber-1]
        # Permitted characters
        result = reader.readtext(image, allowlist='0123456789secSEC', paragraph=False)
        if len(result):
            for (bbox, text, prob) in result:
                if text == '':
                    continue
                # Remove unwanted text
                if 'sec' in text:
                    text = text.replace('s', '').replace('e', '').replace(
                        'c', '').replace('S', '').replace('E', '').replace('C', '')
                    if text == '':
                        continue
                    text = int(text)
                    if text >= 45:
                        continue
                    print(text)
                    matchCount = matchCount + 1
                    foundData.append(text)
                    imageNumber.append(loopNumber)
                    queuedImage.put(image)
        else:
            foundData.append(0)
            imageNumber.append(loopNumber)
            # time.sleep(0.5)
    imageNumber.append((imageNumber[-1]+1))
    foundData.append(0)
    foundData.append(0)
    imageNumber.append(imageCount)
    print('found ' + str(matchCount) + ' total matches')
    save(foundData, imageNumber)

    graph(foundData, imageNumber)


def save(matchedImages, matchingImages):
    np.save('outputdata/tacData.npy', np.vstack((matchedImages, matchingImages)))


def graph(foundData, imageNumber):
    total = imageNumber[-1]
    #del matchingImages[-1]
    x, y = (smoothing(foundData, imageNumber))
    plt.plot(x, y)
    plt.xlabel("Time")
    plt.ylabel("Cool Down")
    plt.xlim([0, total])
    plt.show()
    plt.pause(99999)


def smoothing(y, x):
    lowess_frac = 0.005  # size of data (%) for estimation =~ smoothing window
    lowess_it = 0
    x_smooth = x
    y_smooth = lowess(y, x, is_sorted=False, frac=lowess_frac, it=lowess_it, return_sorted=False)
    return x_smooth, y_smooth


def similar(a, b):
    return jellyfish.jaro_winkler_similarity(a, b)


def display(queuedImage):
    cv2.namedWindow('tacTracker')
    cv2.imshow("tacTracker", cv2.imread('inputData/default.png'))
    while True:
        if not queuedImage.empty():
            cv2.imshow("tacTracker", queuedImage.get())
            continue
        cv2.waitKey(1)


if __name__ == '__main__':
    print('Starting tac tracker')
    queuedImage = multiprocessing.Queue()
    pathToImages = 'inputData/playerTac/'
    process1 = multiprocessing.Process(target=playerTacTracker, args=(pathToImages, queuedImage,))
    process2 = multiprocessing.Process(target=display, args=(queuedImage,))
    process1.start()
    process2.start()
