# cython: profile=True
import csv
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
import glob
import cProfile
from util.apexUtils import ApexUtils as util
import multiprocessing
import tqdm


class miniMapPlotter:
    __slots__ = ['MIN_MATCH_COUNT', 'featureMappingAlgMiniMap', 'featureMatcher', 'mapKeyPoints', 'mapMatching', 'polysizeArray', 'polyTolerance', 'line_color',
                 'line_thickness', 'map_name', 'game_image_ratio', 'game_map_image', 'results', 'resultImageNumber', 'mapFolderPath', 'outputMapPath', 'apex_utils']

    def __init__(self, given_map, ratio):
        # Set up the live image preview window
        plt.axis('off')
        self.apex_utils = util()
        # Pick the map for the program to use
        self.map_name = ''
        self.game_image_ratio = ''
        self.game_map_image = ''
        # Initialize the image handling variables
        self.results = []
        self.resultImageNumber = []
        self.mapFolderPath = self.apex_utils.get_path_to_images()+'minimap/'
        self.outputMapPath = 'outputData/'
        # Minimum number of matching key points between two image
        self.MIN_MATCH_COUNT = 11
        # Initialize the feature mapping algorithm and matcher
        self.featureMappingAlgMiniMap = cv2.SIFT_create()
        self.featureMatcher = cv2.BFMatcher_create(normType=cv2.NORM_L2SQR)
        # Initialize the key point arrays
        self.mapMatching = []
        # Initialize the polygon size array
        self.polysizeArray = [650000, 650000, 560000, 340000, 540000, 440000, 600000]
        self.polyTolerance = 0.5
        self.line_color = (225, 0, 255)
        self.line_thickness = 3
        self.map_name = given_map
        self.game_image_ratio = ratio

    def setupMap(self):
        self.loadMapKeyPoints('src/internal/packedKeypoints/'+self.game_image_ratio+'/' +
                              self.map_name+self.game_image_ratio+'KeyPoints.npy')
        self.game_map_image = cv2.imread('src/internal/maps/'+self.game_image_ratio +
                                         '/map'+self.map_name+self.game_image_ratio+'.jpg')

    def main(self):
        if self.map_name == '' or self.game_image_ratio == '':
            raise Exception('Map or ratio not set')
        self.setupMap()
        end = multiprocessing.Value('i', 0)
        queued_image = multiprocessing.Queue()
        self.apex_utils.display(queued_image, end, 'Minimap Plotter')
        self.miniMapPlotter(queued_image, end)

    def loadMapKeyPoints(self, keypointPath):
        # Load baked key points
        print('Loading Map Data')
        # Load the packed numpy file
        mapKeyPoints = np.load(keypointPath).astype('float32')
        # Split the key points into their respective arrays
        tempKeyPoints = mapKeyPoints[:, :7]
        descriptors = np.array(mapKeyPoints[:, 7:])
        # Create a list of key points
        keyPoints = [cv2.KeyPoint(x, y, _size, _angle, _response, int(_octave), int(_class_id))
                     for x, y, _size, _angle, _response, _octave, _class_id in list(tempKeyPoints)]
        self.mapKeyPoints = {'keyPoints': keyPoints, 'descriptors': descriptors}

    def miniMapPlotter(self, queued_image, end):
        print('Starting matching')
        line = []
        # Loop through the mini map images
        files = self.apex_utils.load_files_from_directory(self.path_to_images)
        with tqdm(files) as pbar:
            for file in pbar:
                frame_number = self.apex_utils.extract_frame_number(file)
                # Load the mini map images
                print(flush=True)
                print("Computing Image " + file.split('\\')[1], end='\n\t')
                image = cv2.imread(file, cv2.IMREAD_COLOR)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                display_image = self.gameMap
                ceterPoint = self.matchImage(image)
                if ceterPoint is not False:
                    line.append(ceterPoint)
                    display_image = self.editImage(display_image, queued_image, line)
                    self.resultImageNumber.append(frame_number)
                    self.results.append(ceterPoint)
        if len(line) == 0:
            print('No matches found, or no images in the folder. Make sure you run the extractMiniMap.py script first')
            return

        print('Average polygon size: %d' %
              (np.sum(self.polysizeArray)/len(self.polysizeArray)), end='\n\t')
        self.save(line)
        end.value = 1

    def editImage(self, display_image, queuedImage, line):
        if len(line) == 0:
            line.append(line[0])
        drawnLine = [np.array(line, np.int32).reshape((-1, 1, 2))]
        print('Updating Display Image', end='\n\t')
        modifiedImage = cv2.polylines(display_image, drawnLine, False, self.color, self.lineThickness, cv2.LINE_AA)
        queuedImage.put(modifiedImage)
        return modifiedImage

    def matchImage(self, image):
        kp1, goodMatches = self.checkIfMatch(image)
        if kp1 is not False:
            ceterPoint, rectanglePoints = self.computeHomography(image, kp1, goodMatches)
            if self.validateMatch(rectanglePoints):
                return np.array(ceterPoint, np.int32)
        return False

    def checkIfMatch(self, image):
        # Initialize the variables
        goodMatches = []
        # compute descriptors and key points on the mini map images
        kp1, des1 = self.featureMappingAlgMiniMap.detectAndCompute(image, None)
        matches = self.featureMatcher.knnMatch(des1, self.descriptors, k=2)
        # Use the ratio test to find good matches
        for m, n in matches:
            if m.distance < 0.65*n.distance:
                goodMatches.append(m)
        if len(goodMatches) >= self.MIN_MATCH_COUNT:
            print('Match found - %d/%d' % (len(goodMatches), self.MIN_MATCH_COUNT), end='\n\t')
            return (kp1, goodMatches)
        else:
            print('Not enough matches found - %d/%d' % (len(goodMatches), self.MIN_MATCH_COUNT), end='\n\t')
            return (False, False)

    def computeHomography(self, image, kp1, goodMatches):
        print('Computing Homography', end='\n\t')
        # Find homography
        src_pts = np.float32([kp1[m.queryIdx].pt for m in goodMatches]).reshape(-1, 1, 2)
        dst_pts = np.float32([self.keyPoints[m.trainIdx].pt for m in goodMatches]).reshape(-1, 1, 2)
        M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w, _ = image.shape
        # create a rectangle around the matching area
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        if M is None:
            return False
        rectanglePoints = cv2.perspectiveTransform(pts, M)
        # Perform a homographic perspective transform on the rectangle of points in order to map the sub image to the main image
        ceterPoint = cv2.perspectiveTransform(np.float32((115, 86)).reshape(-1, 1, 2), M)
        return ceterPoint, rectanglePoints

    def validateMatch(self, rectanglePoints):
        print('Validating Match', end='\n\t')
        # Calculate the size of the newly transformed polygon
        polySize = np.int_(cv2.contourArea(rectanglePoints))
        # Use a rolling average to avoid hard coding size restrictions
        rolling_avg = np.int_((np.sum(self.polysizeArray[-5:-1])/4))
        if polySize != 0:
            self.polysizeArray.append(polySize)
        # Check if the polygon size is within the tolerance of the rolling average
        if polySize > np.int_(rolling_avg+rolling_avg*self.polyTolerance) or polySize < np.int_(rolling_avg-rolling_avg*self.polyTolerance):
            print('Polygon size out of tolerance - %d/%d' % (polySize, rolling_avg), end='\n\t')
            self.polysizeArray.pop()
            return False
        else:
            print('Polygon size within tolerance - %d/%d' % (polySize, rolling_avg), end='\n\t')
            return True

    def save(self, line):
        save_array_data = []
        save_array_frame = []
        for i in range(len(self.results)):
            save_array_data.append((self.results[i][0][0][0], self.results[i][0][0][1]))
            save_array_frame.append(self.resultImageNumber[i])
        self.apex_utils.save(save_array_data, save_array_frame, ['Frame', 'Coords'], 'miniMapPlotter')
        print('Data save complete', end='\n\t')
        print('Saving Image', end='\n\t')
        finalOutputBase = self.gameMap
        # Draw all the center points with lines connecting them on the main image
        finalOutputBase = cv2.polylines(finalOutputBase, [np.array(line, np.int32).reshape(
            (-1, 1, 2))], False, self.color, self.lineThickness, cv2.LINE_AA)
        finalOutputBase = cv2.cvtColor(finalOutputBase, cv2.COLOR_BGR2RGB)
        plt.imsave(self.outputMapPath + ' FINAL' + '.jpg', finalOutputBase)
        print('Image save complete', end='\n\t')
        print('Program complete', end='\n\t')


if __name__ == '__main__':
    miniMapMatching = miniMapPlotter('BM', '4by3')
    miniMapMatching.main()
