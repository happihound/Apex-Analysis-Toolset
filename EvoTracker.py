import time
import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
import easyocr
from tqdm import tqdm
from statsmodels.nonparametric.smoothers_lowess import lowess


plt.switch_backend('TKAgg')
plt.bbox_inches = "tight"


def evoTracker(pathToImages, queuedImage, end):
    # Define variables
    end.value = 0
    matchCount = 0
    loopNumber = 0
    imageCount = 0
    foundData = []
    imageNumber = []
    foundData.append(0)
    imageNumber.append(0)

    # Get image count
    for _ in glob.glob(pathToImages + '/*.png'):
        imageCount = imageCount + 1
    print('Number of evo images to match ' + str(imageCount))

    # Create the easyocr reader
    reader = easyocr.Reader(['en'])

    # Use tqdm to display a progress bar
    pbar = tqdm(glob.glob(pathToImages + '/*.png'))

    # Loop through all evo images
    for file in pbar:
        image = cv2.imread(file)
        loopNumber = loopNumber + 1

        # Define permitted characters
        result = reader.readtext(
            image, allowlist='0123456789', paragraph=False)

        # Check if the image matches the expected format
        if check_match(result, loopNumber, foundData, imageNumber, pbar, matchCount):
            # Add the image to the queue
            queuedImage.put(image)
            matchCount = matchCount + 1

    # Add the final data to the arrays
    imageNumber.append((imageNumber[-1] + 1))
    foundData.append(0)
    foundData.append(0)
    foundData = filterValues(foundData)
    imageNumber.append(imageCount)
    print('found ' + str(matchCount) + ' total matches')

    # Save the data
    save(foundData, imageNumber)

    # Graph the data
    graph(foundData, imageNumber)
    # End the program
    end.value = 1


def check_match(result, loopNumber, foundData, imageNumber, pbar, matchCount):
    # For each result in the result list
    for (bbox, text, prob) in result:
        # If there is no text ignore it
        if not text:
            continue
        # Convert the text to a number
        evoFound = int(text)
        # Needs at 98% or great probability of being accurate
        if (prob > 0.98):
            # Max value of an EVO
            if (evoFound > 751):
                print('bad match, over 750')
                continue
            # Update the progress bar
            pbar.set_description(desc=str(matchCount), refresh=True)
            # Add the data to the lists
            foundData.append(evoFound)
            imageNumber.append(loopNumber)
            # Return true to say we found a match
            return True
    # Return false to say we didn't find a match
    return False


def save(matchedImages, matchingImages):
    np.save('outputdata/evoData.npy',
            np.vstack((matchedImages, matchingImages)))


def filterValues(values):
    # Make a copy of the list to avoid changing the original
    newValues = values.copy()

    # Loop through the list, skipping the first and last values
    for i in range(1, len(values) - 1):
        # If the next value is the same as the previous value, set the current value to that value
        if values[i - 1] == values[i + 1]:
            newValues[i] = values[i - 1]

    # Return the new list
    return newValues


def graph(foundData, imageNumber):
    # Creates a graph
    total = imageNumber[-1]
    x, y = (smoothing(foundData, imageNumber))
    plt.plot(x, y)
    plt.xlabel("Time")
    plt.ylabel("Damage to level up")
    plt.xlim([0, total])
    plt.show()


def smoothing(y, x):
    # Smooth the data
    # fraction of data to be used for estimating the smoothed values
    lowess_frac = 0.0001
    # number of iterations for the lowess algorithm
    lowess_it = 0
    # set x_smooth to be the same as x
    x_smooth = x
    # calculate smoothed values
    y_smooth = lowess(y, x, is_sorted=False, frac=lowess_frac,
                      it=lowess_it, return_sorted=False)
    return x_smooth, y_smooth


def display(queuedImage, end):
    time.sleep(1)
    cv2.namedWindow('evoTracker')
    cv2.imshow("evoTracker", cv2.imread('inputData/default.png'))
    while not end.value:
        if not queuedImage.empty():
            cv2.imshow("evoTracker", queuedImage.get())
            continue
        cv2.waitKey(1)


def main():
    print('Starting evo tracker')
    queuedImage = multiprocessing.Queue()
    end = multiprocessing.Value("i", False)
    pathToImages = 'inputData/playerEvo/'
    process1 = multiprocessing.Process(
        target=evoTracker, args=(pathToImages, queuedImage, end))
    process2 = multiprocessing.Process(target=display, args=(queuedImage, end))
    process1.start()
    process2.start()
    process1.join()
    process2.join()
    print('Finished evo tracker')


if __name__ == '__main__':
    main()
