import csv
import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import jellyfish
import easyocr
from src.util.apexUtils import ApexUtils as util
from tqdm import tqdm
plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"
# To-do increase size of killfeedbox read area
scale_percent = 200  # percent of original size


def killFeedFinder(pathToImages, queuedImage):
    apex_utils = util.ApexUtils()
    matchCount = 0
    averageProb = 0
    countForProb = 0
    loopNumber = 0
    imageCount = 0
    imageNumber = []
    foundData = []
    foundImageNames = []
    wholeFoundText = []
    allImages = []
    reader = easyocr.Reader(['en'], gpu=True)
    # Count all images in the folder
    for file in glob.glob(pathToImages + '/*.png'):
        imageCount = imageCount + 1
    print('Number of killFeed images to match ' + str(imageCount))
    for file in glob.glob(pathToImages + '/*.png'):
        image = cv2.imread(file)
        # Define targets and exclusions for the OCR to find or ignore
        myTeamUserNames = ['happihound', 'tictaks_x', 'steady', 'steadman', '[BETR]']
        secondaryTargetStrings = ['ttv', 'tv', 'twitch', 'youtube', 'live']
        excludedTargets = ['reviving', 'entered', 'landed', 'crafting']
        # Locate the killfeed box
        textLocation = reader.detect(image, width_ths=10000, height_ths=10000, slope_ths=10000, ycenter_ths=10000)
        if not empty_tree(textLocation):
            colL, colH = textLocation[0][0][0][0], textLocation[0][0][0][1]
            rowL, rowH = textLocation[0][0][0][2], textLocation[0][0][0][3]
            if rowL < 0:
                rowL = 0
            if colL < 0:
                colL = 0
            if rowH > image.shape[0]:
                rowH = image.shape[0]
            if colH > image.shape[1]:
                colH = image.shape[1]
            # Crop the image to the area of the killfeed
            image = image[rowL:rowH, colL:colH]
            # denoise the image
            width = int(image.shape[1] * scale_percent / 100)
            height = int(image.shape[0] * scale_percent / 100)
            dim = (width, height)
            image1 = cv2.UMat(image)
            # Resize the image to increase the OCR accuracy
            image1 = cv2.resize(image1, dim, interpolation=cv2.INTER_CUBIC)
            image = image1.get()
            result = reader.readtext(image, batch_size=8,
                                     detail=1, width_ths=10000, height_ths=1, slope_ths=3, paragraph=False)
            print(result)
            exit()
            # draw boxed around the text
            for (bbox, text, prob) in result:
                if type(bbox[0][0]) != np.int32:
                    continue
                cv2.rectangle(image, (bbox[0][0], bbox[0][1]), (bbox[2][0], bbox[2][1]), (0, 255, 0), 2)
            queuedImage.put(image)
        else:
            queuedImage.put(image)
            loopNumber = loopNumber + 1
            continue
        validCheck = True
        teamUserNames = []
        enemyUserNames = []
        # Read the tuple from the OCR output
        for (bbox, text, prob) in result:
            print(text)
            text = text.split(' ')
            for word in text:
                for username in myTeamUserNames:
                    if similar(word, username) > 0.9:
                        teamUserNames.append(word)
                        averageProb = averageProb + prob
                        countForProb = countForProb + 1
                        wholeFoundText.append(text)
                        word.replace(word, '')
                for textScrap in secondaryTargetStrings:
                    if textScrap in word:
                        enemyUserNames.append(word)
                        averageProb = averageProb + prob
                        countForProb = countForProb + 1
                        word.replace(word, '')
                for excluded in excludedTargets:
                    if excluded in word:
                        word.replace(word, '')
        # Remove similar strings from the list
        for string in teamUserNames:
            removeSimilar(teamUserNames, string)
        for string in enemyUserNames:
            removeSimilar(enemyUserNames, string)
        # Check if the OCR found any valid data
        print("Teammaates: ", end="")
        print(teamUserNames)
        if len(teamUserNames) == 0:  # or len(enemyUserNames) == 0:
            validCheck = False
        # If the OCR found valid data, save the image and the data
        if validCheck:
            print(((str(file).split('\\')[-1].split('Apex Legends')[1])), end=", ")
            # cv2.imwrite('other/otherOutput/' +
           #             (((str(file).split('\\')[-1].split('Apex Legends')[1]))), image)
            # print(enemyUserNames[-1], end=", ")
            print(text, end=", ")
            matchCount = matchCount + 1
            foundData.append(text)
            foundImageNames.append((((str(file).split('\\')[-1].split('Apex Legends')[1]))))
            imageNumber.append(loopNumber)
            queuedImage.put(image)
        loopNumber = loopNumber + 1
    print(foundData)
    save(foundData, imageNumber)
    # save all results to a csv file with the image name with whole text
    with open('other/otherOutput/killFeedData.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Image Name", "Text"])
        for i in range(len(foundData)):
            writer.writerow([foundImageNames[i], foundData[i]])
    print("Found " + str(matchCount) + " matches")
    print("average prob was " + str(averageProb/countForProb))
    print('DONE MATCHING')


def save(foundData, imageNumber):
    np.save('other/otheroutput/KillFeedData1.npy',
            np.vstack((foundData, imageNumber)))
    pass


def similar(inputStringOne, inputStringTwo):
    # Check similarity between targets and results
    otherTargets = ['happi', 'happl', 'bappi', 'hound', 'appi', 'appl', "hppi"]
    similarity = jellyfish.jaro_winkler_similarity(
        inputStringOne, inputStringTwo)
    inputStringOne = inputStringOne.lower()
    inputStringTwo = inputStringTwo.lower()
    if len(inputStringOne) == len(inputStringTwo) or len(inputStringOne) == len(inputStringTwo) - 1 or len(inputStringOne) == len(inputStringTwo) + 1 or len(inputStringOne) == len(inputStringTwo) - 2 or len(inputStringOne) == len(inputStringTwo) + 2:
        similarity = similarity + 0.15
    for targets in otherTargets:
        if ((jellyfish.jaro_winkler_similarity(inputStringOne, targets) > 0.7)):
            similarity = similarity + 0.2
            break
    return similarity


def removeSimilar(inputList, stringToCheck):
    # Remove similar strings from the list
    for string in inputList:
        if (similar(string, stringToCheck) > 0.8):
            inputList.remove(string)
    return inputList


def empty_tree(input_list):
    for item in input_list:
        if not isinstance(item, list) or not empty_tree(item):
            return False
    return True


def main():
    print('Starting Kill Feed Elimination Finder')
    pathToImages = "C:/pythonTestArea/other/images"
    queuedImage = multiprocessing.Queue()
    process1 = multiprocessing.Process(
        target=killFeedFinder, args=(pathToImages, queuedImage,))
    process2 = multiprocessing.Process(target=(util.display), args=(queuedImage,))
    process1.start()
    process2.start()


if __name__ == '__main__':
    main()
