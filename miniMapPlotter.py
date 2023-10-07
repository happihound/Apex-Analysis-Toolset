import csv
import sys
import numpy as np
import cv2 as cv
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import cProfile
import multiprocessing


class miniMapPlotter:
    __slots__ = ['map', 'mapPath', 'gameMap', 'images', 'results', 'resultImageNumber', 'mapFolderPath', 'outputMapPath', 'MIN_MATCH_COUNT', 'featureMappingAlgMiniMap', 'featureMatcher',
                 'mapKeyPoints', 'ratio', 'tempKeyPoints', 'numberOfImagesRun', 'matchCountForStats', 'descriptors', 'keyPoints', 'polysizeArray', 'polyTolerance', 'matches', 'editedImage', 'color', 'lineThickness', 'dst_line_final', 'queuedImage', 'end']

    def __init__(self):
        # Set up the live image preview window
        plt.bbox_inches = "tight"
        plt.switch_backend('TKAgg')
        plt.axis('off')
        # Pick the map for the program to use
        self.map = ''
        self.ratio = ''
        self.mapPath = ''
        self.gameMap = ''
        # Initialize the image handling variables
        self.images = []
        self.results = []
        self.resultImageNumber = []
        self.mapFolderPath = 'input/minimap/'
        self.outputMapPath = 'outputData/'
        # Minimum number of matching key points between two image
        self.MIN_MATCH_COUNT = 13
        # Initialize the feature mapping algorithm and matcher
        self.featureMappingAlgMiniMap = None
        self.featureMatcher = None
        # Initialize the key point arrays
        self.mapKeyPoints = []
        self.tempKeyPoints = []
        self.descriptors = []
        self.keyPoints = []
        # Initialize the polygon size array
        self.polysizeArray = [650000, 650000, 560000, 340000, 540000, 440000, 600000]
        self.polyTolerance = 0.5
        self.matches = 0
        self.numberOfImagesRun = 0
        self.matchCountForStats = 0
        self.editedImage = []
        self.color = (225, 0, 255)
        self.lineThickness = 3
        self.queuedImage = multiprocessing.Queue()
        self.end = multiprocessing.Value('i', 0)

    def setMap(self, map):
        self.map = map
        self.mapPath = 'internal/packedKeypoints/'+self.ratio+'/'+self.map+self.ratio+'KeyPoints.npy'

    def setRatio(self, ratio):
        self.ratio = ratio
        self.setMap(self.map)

    def main(self):
        self.gameMap = cv2.imread('internal/maps/'+self.ratio+'/map'+self.map+self.ratio+'.jpg')
        process1 = multiprocessing.Process(target=self.miniMapPlotter, args=(self.queuedImage, self.end,))
        process2 = multiprocessing.Process(target=self.display, args=(self.queuedImage, self.end,))
        process1.start()
        process2.start()

    def loadMapKeyPoints(self, keypointPath):
        # Load baked key points
        print('Loading Map Data')
        # Load the packed numpy file
        self.mapKeyPoints = np.load(keypointPath).astype('float32')
        # Split the key points into their respective arrays
        self.tempKeyPoints = self.mapKeyPoints[:, :7]
        self.descriptors = np.array(self.mapKeyPoints[:, 7:])
        # Create a list of key points
        self.keyPoints = [cv2.KeyPoint(x, y, _size, _angle, _response, int(_octave), int(_class_id))
                          for x, y, _size, _angle, _response, _octave, _class_id in list(self.tempKeyPoints)]

    def miniMapPlotter(self, queuedImage, end):
        self.featureMappingAlgMiniMap = cv.SIFT_create()
        self.featureMatcher = cv.BFMatcher_create(normType=cv.NORM_L2SQR)
        print('Starting matching')
        # Initialize the variables
        try:
            self.loadMapKeyPoints(self.mapPath)
        except:
            print('No map data found, make sure to run the mapDataPacker first')
            sys.exit()
        line = []
        # Loop through the mini map images
        for imageNumber, file in enumerate(glob.glob(self.mapFolderPath + '/*.png')):
            # Load the mini map images
            print(flush=True)
            print("Computing Image " + file.split('\\')[1], end='\n\t')
            self.numberOfImagesRun = self.numberOfImagesRun + 1
            image = cv.imread(file, cv2.IMREAD_COLOR)
            self.editedImage = self.gameMap.copy()
            ceterPoint = self.matchImage(image)
            if ceterPoint is not False:
                line.append(ceterPoint)
                self.editImage(queuedImage, line)
                self.resultImageNumber.append(imageNumber)
                self.results.append(ceterPoint)
        if len(line) == 0:
            print('No matches found, or no images in the folder. Make sure you run the extractMiniMap.py script first')
            sys.exit()

        self.save(line)
        end.value = 1
        sys.exit()

    def editImage(self, queuedImage, line):
        if len(line) == 0:
            line.append(line[0])
        drawnLine = [np.array(line, np.int32).reshape((-1, 1, 2))]
        print('Updating Display Image', end='\n\t')
        modifiedImage = cv.polylines(self.editedImage, drawnLine, False, self.color, self.lineThickness, cv.LINE_AA)
        queuedImage.put(modifiedImage)
        self.editedImage = modifiedImage

    def matchImage(self, image):
        kp1, goodMatches = self.checkIfMatch(image)
        if kp1 is not False:
            ceterPoint, rectanglePoints = self.computeHomography(image, kp1, goodMatches)
            if self.validateMatch(rectanglePoints):
                return np.array(ceterPoint, np.int32)
        return False

    def checkIfMatch(self, image):
        # Initialize the variables
        lastPoint = []
        goodMatches = []
        # compute descriptors and key points on the mini map images
        kp1, des1 = self.featureMappingAlgMiniMap.detectAndCompute(image, None)
        matches = self.featureMatcher.knnMatch(des1, self.descriptors, k=2)
        # Use the ratio test to find good matches
        for m, n in matches:
            if m.distance < 0.65*n.distance:
                goodMatches.append(m)
        self.matchCountForStats += len(goodMatches)
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
        M, _ = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
        h, w, _ = image.shape
        # create a rectangle around the matching area
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        rectanglePoints = cv.perspectiveTransform(pts, M)
        if M is None:
            return False
        # Perform a homographic perspective transform on the rectangle of points in order to map the sub image to the main image
        ceterPoint = cv.perspectiveTransform(np.float32((115, 86)).reshape(-1, 1, 2), M)
        return ceterPoint, rectanglePoints

    def validateMatch(self, rectanglePoints):
        print('Validating Match', end='\n\t')
        # Calculate the size of the newly transformed polygon
        polySize = np.int_(cv.contourArea(rectanglePoints))
        # Use a rolling average to avoid hard coding size restrictions
        rolling_avg = int((np.sum(self.polysizeArray[-4:-1])/3))
        if polySize != 0:
            self.polysizeArray.append(polySize)
        # Check if the polygon size is within the tolerance of the rolling average
        if polySize > int(rolling_avg+rolling_avg*self.polyTolerance) or polySize < int(rolling_avg-rolling_avg*self.polyTolerance):
            print('Polygon size out of tolerance - %d/%d' % (polySize, rolling_avg), end='\n\t')
            return False
        else:
            print('Polygon size within tolerance - %d/%d' % (polySize, rolling_avg), end='\n\t')
            return True

    def save(self, line):
        print('Saving data')
        print('Average matches per image: %d' %
              (self.matchCountForStats/self.numberOfImagesRun), end='\n\t')
        # Save the data to a csv file
        with open(self.outputMapPath + 'output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['Image Number', 'X', 'Y'])
            for i in range(len(self.results)):
                writer.writerow([self.resultImageNumber[i], self.results[i][0][0][0], self.results[i][0][0][1]])
        print('Data save complete', end='\n\t')
        print('Saving Image', end='\n\t')
        finalOutputBase = self.gameMap.copy()
        # Draw all the center points with lines connecting them on the main image
        finalOutputBase = cv.polylines(finalOutputBase, [np.array(line, np.int32).reshape(
            (-1, 1, 2))], False, self.color, self.lineThickness, cv.LINE_AA)
        finalOutputBase = cv2.cvtColor(finalOutputBase, cv2.COLOR_BGR2RGB)
        plt.imsave(self.outputMapPath + ' FINAL' + '.jpg', finalOutputBase)
        print('Image save complete', end='\n\t')
        print('Program complete', end='\n\t')

    def display(self, queuedImage, end):
        print('Displaying', end='\n\t')
        cv2.namedWindow('mapImage', cv2.WINDOW_NORMAL)
        cv2.imshow("mapImage", self.gameMap)
        while end.value == 0:
            if not queuedImage.empty():
                imS = cv2.resize(queuedImage.get(), (1333, 1000))
                cv2.imshow("mapImage", imS)
                continue
            cv2.waitKey(1)


if __name__ == '__main__':
    print('Starting MiniMap Matching')
    #args = sys.argv
    # Debug arguments for testing
    args = ['miniMapPlotting.py', '-mapName=OLY', '-ratio=4by3']
    # Check if the user has entered the correct number of arguments
    if len(args) == 1:
        print("Command format:")
        print("\tminiMapPlotting.py -mapName=MAPNAME -ratio=RATIO")
        print("\t\t-mapName: Name of the map to be used, valid names are:")
        print("\t\t\t- 'KC'")
        print("\t\t\t- 'WE'")
        print("\t\t\t- 'OLY'")
        print("\t\t\t- 'SP'")
        print("\t\t\t- 'BM'")
        print("\t\t -ratio (optional): Aspect ratio of the map, valid ratios are:")
        print("\t\t\t- '4by3' (default)")
        print("\t\t\t- '16by9' ")
        print("\t\t\t- '16by10'")
    else:
        args.pop(0)
        # Create a miniMapPlotter object and set the map name and aspect ratio
        miniMapMatching = miniMapPlotter()
        for arg in args:
            if arg.split('=')[0] == '-mapName':
                miniMapMatching.setMap(arg.split('=')[1])
            elif arg.split('=')[0] == '-ratio':
                miniMapMatching.setRatio(arg.split('=')[1])
            else:
                print("Invalid argument: " + arg)
                exit()

    miniMapMatching.main()
