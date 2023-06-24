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
        "__thresheldImage", "__targets", "__imageOriginalImage", "__croppedImage"]

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

        # Get the thresheld image
        self.__thresheldImage = gameMapImage(self.__makeThresholdImage(), "1:1")

        # Find the red dots
        # self.__targets = self.__findRedDots()

    def getThresheldImage(self) -> gameMapImage:
        if self.__thresheldImage is None:
            self.__thresheldImage = gameMapImage(self.__makeThresholdImage(), "1:1")
        return self.__thresheldImage

    def getOriginalImage(self) -> gameMapImage:
        return self.__imageOriginalImage

    def getCroppedImage(self) -> gameMapImage:
        return self.__croppedImage

    def getValidRatios(self) -> list[str]:
        return ["1:1", "4:3", "16:9", "16:10", "1by1", "4by3", "16by9", "16by10"]

    def getTargets(self) -> list:
        return self.__targets

    def __findZoneCircle(self) -> list:
        pass

    def __makeThresholdImage(self) -> np.ndarray:
        # convert to hsv
        editedImage = self.__croppedImage.image()
        self.__thresheldImage = self.getCroppedImage().copy()

        # perform binary thresholdin
        mask = cv.threshold(editedImage, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

        # set the threshold image to mask
        self.__thresheldImage = gameMapImage(mask, "1:1")

        return self.__thresheldImage.image()

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
        scalarDict = {"4:3": (192/1920, 283/1920, 62/1080), "16:10": (315/1680, 379 /
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
