import math
import cv2 as cv
import numpy as np
import imutils
from gameMapImage import gameMapImage

# Takes a cv2 image and returns a cv2 image
# finds the corners of the map from the full image
# Returns a cropped image of only the map


class userMapImage:
    __slots__ = [
        "__targets", "__imageOriginalImage", "__croppedImage"]

    def __init__(self, cv2Image: np.ndarray, ratio: str = "") -> None:
        self.__imageOriginalImage = gameMapImage(cv2Image, ratio)
        # If the aspect ratio is not set, detect it from the image
        if ratio not in self.getValidRatios() and ratio != "":
            raise ValueError(
                f"Invalid aspect ratio. Valid ratios are {self.getValidRatios()}")
        if self.__imageOriginalImage.ratio() == "":
            self.__imageOriginalImage = gameMapImage(self.__imageOriginalImage(), self.__detectAspectRatio())
        # Determine the crop size by the aspect ratio
        cropSize = self.__returnCropSize(self.__imageOriginalImage.shape(), self.__imageOriginalImage.ratio())

        # Change the image aspect ratio
        self.__croppedImage = gameMapImage(self.__changeImageAspectRatio(
            self.__cropImage(self.__imageOriginalImage(), cropSize)), "1:1")

    def getOriginalImage(self) -> gameMapImage:
        return self.__imageOriginalImage

    def getCroppedImage(self) -> gameMapImage:
        return self.__croppedImage

    def getValidRatios(self) -> list[str]:
        return ["1:1", "4:3", "16:9", "16:10", "1by1", "4by3", "16by9", "16by10"]

    def getTargets(self) -> list:
        return self.__targets

    def extractZone(self) -> list:
        # This will work for all normal ratios, but since 4:3 is kinda broken, we need to do something else that will tolerate semi-circle zones
        if self.__imageOriginalImage.ratio() == "4:3" or self.__imageOriginalImage.ratio() == "4by3":
            return self.__extractZone4by3()
        # Convert the image to grayscale
        gray = cv.cvtColor(self.__croppedImage(), cv.COLOR_BGR2GRAY)
        # Blur the image
        blurred = cv.GaussianBlur(gray, (5, 5), 0)
        # Find the circles

        dp = 0.5
        minDist = 200
        param1 = 5
        param2 = 100
        maxRadius = int(self.getCroppedImage().shape()[0] // 3.7)
        minRadius = int(maxRadius*0.25)
        circles = cv.HoughCircles(blurred, cv.HOUGH_GRADIENT, dp, minDist, param1=param1,
                                  param2=param2, minRadius=minRadius, maxRadius=maxRadius)

        # Convert the circles to a list
        circles = np.round(circles[0, :]).astype("int")
        # Return the circles
        return circles

    def __extractZone4by3(self) -> list:
       # gray = cv.cvtColor(self.__croppedImage(), cv.COLOR_BGR2GRAY)
     # Load the image
        img = self.__croppedImage()

        #do canny image detection
        edges = cv.Canny(img, 100, 200)

        #draw edges
        cv.imshow("edges", edges)
        cv.waitKey(0)

        #find contours
        contours, hierarchy = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

  
        M = cv.moments(max_contour)


        # Display the result
        cv.imshow("Result", result)
        cv.waitKey(0)
        cv.destroyAllWindows()
        # Apply a threshold to the image to create a binary image
        # _, thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
        # cv.imshow("thresh", thresh)
        # cv.waitKey(0)
        # # Find contours in the binary image
        # contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        # # Loop over the contours and find the one with the largest area
        # max_area = 0
        # max_contour = None
        # for contour in contours:
        #     area = cv.contourArea(contour)
        #     if area > max_area:
        #         max_area = area
        #         max_contour = contour

        # # Fit a circle to the contour
        # (x, y), radius = cv.minEnclosingCircle(max_contour)
        # center = (int(x), int(y))
        # radius = int(radius)

        # return [(center[0], center[1], radius)]

    def __remove(self, the_list: list, val) -> list:
        return [value for value in the_list if value != val]

    def __detectAspectRatio(self) -> str:
        height, width, channels = self.__imageOriginalImage.shape()
        if height * 4 == width * 3:
            return "4:3"
        if height * 16 == width * 10:
            return "16:10"
        if height * 16 == width * 9:
            return "16:9"
        raise ValueError("Invalid aspect ratio", height, width)

    def __cropImage(self, image: np.ndarray, cropSize: tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]) -> np.ndarray:
        # Extract the four corners of the cropping rectangle
        topLeft, topRight, bottomLeft, bottomRight = cropSize
        # Crop the image
        croppedImage = image[topLeft[1]: bottomLeft[1], topLeft[0]: topRight[0]]
        return croppedImage

    def __returnCropSize(self, imageShape: tuple[int, int, int], ratio: str) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
        # The image shape is a tuple with height, width, and channels
        height, width, channels = imageShape
        # The dictionary is in the format {aspectRatio: (leftMarginRatio, righMarginRatip, bottomMarginRatio)}
        # The aspect ratio is defined as the width divided by the height
        # The ratios are defined as the ratio of the margin width or height to the width or height of the image
        if "by" in ratio:
            ratio = ratio.replace("by", ":")
        scalarDict = {"4:3": (240/1920, 325/1920, 85/1440), "16:10": (315/1680, 379 /
                                                                      1680, 62/1050), "16:9": (420/1920, 485/1920, 64/1080)}
        if ratio not in scalarDict:
            raise ValueError("Invalid aspect ratio", ratio)
        leftWidthRatio, rightWidthRatio, bottomHeightRatio = scalarDict[ratio]
        rightWidth = int(width * rightWidthRatio)
        leftWidth = int(width * leftWidthRatio)
        bottomHeight = int(height * bottomHeightRatio)
        topLeft = (leftWidth, 0)
        topRight = (width - rightWidth, 0)
        bottomLeft = (leftWidth, height - bottomHeight)
        bottomRight = (width - rightWidth, height - bottomHeight)
        return (topLeft, topRight, bottomLeft, bottomRight)

    def __changeImageAspectRatio(self, image: np.ndarray) -> np.ndarray:
        # resize image to desired height
        image = cv.resize(image, (image.shape[0], image.shape[0]), interpolation=cv.INTER_AREA)
        # resize image to desired width
        image = cv.resize(image, (800, 800), interpolation=cv.INTER_AREA)
        return image

    def __call__(self) -> gameMapImage:
        return self.__imageOriginalImage

    # Path: gameMapImage.py
