import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import jellyfish
import easyocr
from tqdm import tqdm
from networkx.algorithms import similarity
plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"


def playerGunFinder(pathToImages, queuedImage):
    matchCount = 0
    loopNumber = 0
    imageCount = 0
    all_Images = []
    imageNumber = []
    foundData = []
    imageNumber.append(0)
    reader = easyocr.Reader(['en'])
    for file in glob.glob(pathToImages + '/*.png'):
        all_Images.append(cv2.imread(file))
        imageCount = imageCount + 1
    print('Number of images to match ' + str(imageCount))
    for _ in tqdm(glob.glob(pathToImages + '/*.png')):
        loopNumber = loopNumber + 1
        image = all_Images[loopNumber - 1]
        # Possible gun names
        gunList = ['R-301', 'HEMLOK', 'FLATLINE', 'HAVOC', 'SPITFIRE', 'DEVOTION', 'RAMPAGE', 'L-STAR', 'BOCEK', 'G7 SCOUT', 'TRIPLE TAKE', '30-30', 'PEACEKEEPER',
                   'MASTIFF', 'EVA-8', 'MOZAMBIQUE', 'CAR', 'R-99', 'PROWLER', 'VOLT', 'ALTERNATOR', 'WINGMAN', 'RE-45', 'P2020', 'LONGBOW', 'SENTINEL', 'KRABER', 'CHARGE RIFLE', 'NEMESIS']
        result = reader.readtext(
            image, paragraph=False, allowlist='012345789ABCDEFGHIJKLMNOPQRSTUVWZ-')
        if len(result) == 2:
            for (bbox, text, prob) in result:
                foundGun = gunSimlarityChecker(gunList, text)
                print(foundGun)
                matchCount = matchCount + 1
                foundData.append(foundGun)
                imageNumber.append(matchCount)
                queuedImage.put(image)
    graph(foundData)

    save(foundData, imageNumber)
    print('DONE MATCHING')


def similar(inputStringOne, inputStringTwo):
    similarity = jellyfish.jaro_winkler_similarity(
        inputStringOne, inputStringTwo)
    if len(inputStringOne) == len(inputStringTwo) or len(inputStringOne) == len(inputStringTwo) - 1 or len(inputStringOne) == len(inputStringTwo) + 1:
        similarity = similarity + 0.1
    else:
        similarity = similarity - 0.2
    return similarity


def gunSimlarityChecker(guns, inputString):
    largestProbValue = 0
    predictedGun = 0
    for gun in guns:
        gunSimlarity = (similar(gun, inputString))
        if gunSimlarity > largestProbValue:
            largestProbValue = gunSimlarity
            predictedGun = gun
    return predictedGun


def filterValues(values):
    loopNumber = 2
    newValues = values.copy()
    for i in values:
        loopNumber = loopNumber + 1
        if loopNumber > len(values) - 2:
            break

        if values[loopNumber - 1] == values[loopNumber + 1]:
            newValues[loopNumber] = values[loopNumber - 1]

    lii_unique = list(set(newValues))
    counts = [newValues.count(value) for value in lii_unique]
    loopNumber = 0
    denoisedValues = newValues.copy()
    for absoluteCount in counts:
        if((absoluteCount / len(denoisedValues) * 200) <= 1.5):
            newValues = remove_values_from_list(
                newValues, lii_unique[loopNumber])
        loopNumber = loopNumber + 1
    return newValues


def remove_values_from_list(the_list, val):
    values = []
    for i in the_list:
        if i != val:
            values.append(i)
    return values



if __name__ == '__main__':
    print('Starting player gun Finder')
    queuedImage = multiprocessing.Queue()
    pathToImages = 'inputData/playerGuns/'
    process1 = multiprocessing.Process(
        target=playerGunFinder, args=(pathToImages, queuedImage,))
    process2 = multiprocessing.Process(target=display, args=(queuedImage,))
    process1.start()
    process2.start()
