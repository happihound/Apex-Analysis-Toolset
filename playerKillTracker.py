import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import easyocr
from statsmodels.nonparametric.smoothers_lowess import lowess
from tqdm import tqdm
import apexUtils
# Similar to evo tracker
apexUtils = apexUtils.apexUtils()
plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"


def killTracker(pathToImages, queuedImage, end):
    matchCount = 0
    loopNumber = 0
    imageCount = 0
    data = []
    time = []
    all_Images = []
    data.append(0)
    time.append(0)
    rollingArray = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
    for file in glob.glob(pathToImages + '/*.png'):
        all_Images.append(cv2.imread(file))
        imageCount = imageCount+1
    print('Number of kill images to match ' + str(imageCount))
    reader = easyocr.Reader(['en'])
    pbar = tqdm(glob.glob(pathToImages + '/*.png'))
    for file in pbar:
        loopNumber = loopNumber + 1
        image = all_Images[loopNumber-1]
        image = imageBinarizer(image)
        result = reader.readtext(image, allowlist='0123456789', paragraph=False)
        queuedImage.put(image)
        if len(result):
            sequenceOfTextFound = 0
            for (bbox, text, prob) in result:
                if text == '':
                    continue
                text = int(text)
                sequenceOfTextFound = sequenceOfTextFound + 1
                if sequenceOfTextFound > 1 or prob < 0.9:
                    continue
                checkValue = int((np.sum(rollingArray[-3:-1])/3))
                #print('checkValue: ' + str(checkValue))
                rollingArray.append(text)
                if ((checkValue > text) or ((checkValue+5) < text)):
                    #print('bad match, found '+str(text) + ' but expected closer to ' + str(checkValue))
                    continue
                #print(str(text) + ' ' + str(prob))
                matchCount = matchCount + 1
                data.append(text)
                time.append(loopNumber)
                queuedImage.put(image)
                pbar.set_description(desc=str(matchCount), refresh=True)
    time.append(imageCount)
    data.append(data[-1])
    data = filterValues(data)
    print('found ' + str(matchCount) + ' total matches')
    apexUtils.save(data=data, time=time, name='killData')
    end.value = 1
    apexUtils.graph(xAxis=time, yAxis=data, yAxisLabel="data", smoothingWindow=0.00001, total=True)


def imageBinarizer(image):
    width = int(image.shape[1] * 5)
    height = int(image.shape[0] * 5)
    dim = (width, height)

    # resize image
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    # Color segmentation
    hsv = cv2.cvtColor(resized, cv2.COLOR_RGB2HSV)
    lower_red = np.array([0, 0, 220])
    upper_red = np.array([200, 45, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(resized, resized, mask=mask)
    return res


def filterValues(values):
    loopNumber = 8
    newValues = values.copy()
    for i in values:
        loopNumber = loopNumber + 1
        if loopNumber > len(values)-4:
            break

        newValues[loopNumber] = most_frequent(values[loopNumber-8:loopNumber+4])
    return newValues


def most_frequent(List):
    counter = 0
    num = List[0]

    for i in List:
        curr_frequency = List.count(i)
        if (curr_frequency > counter):
            counter = curr_frequency
            num = i

    return num


def main():
    print('Starting kill tracker')
    queuedImage = multiprocessing.Queue()
    pathToImages = 'inputData/playerKills/'
    end = multiprocessing.Value("i", False)
    process1 = multiprocessing.Process(target=killTracker, args=(pathToImages, queuedImage, end))
    process2 = multiprocessing.Process(target=apexUtils.display, args=(queuedImage, end, 'Kill Tracker'))
    process1.start()
    process2.start()


if __name__ == '__main__':
    main()
