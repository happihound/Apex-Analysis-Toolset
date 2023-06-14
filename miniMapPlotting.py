import numpy as np
import cv2 as cv
import cv2 as cv2
import matplotlib.pyplot as plt
import glob
import multiprocessing
from tqdm import tqdm
gameMap = 'maps/mapWE4by3.png'
def miniMapPlotter(queuedImage):
    #import the main image that other images should map to 
    plt.switch_backend('TKAgg')
    editedImage = cv2.imread(gameMap)
    #minimum number of matching key points between two images 
    MIN_MATCH_COUNT = 12
    mapFolderPath = 'inputData/miniMap/'
    outputMapPath = 'outputData/outputMinimap/'
    plt.bbox_inches="tight"
    picNumber = 0
    matchNumber = 0
    miniMapNumber = 0
    imageNumber = []
    foundData = []
    featureMappingAlgMiniMap = cv.SIFT_create()
    featureMatcher = cv.BFMatcher_create(normType=cv.NORM_L2SQR)
    all_images = []
    print('Loading Full Map Data')
    #load baked key points
    bigMapDataArray = np.load('packedKeypoints/we4by3KeyPoints.npy').astype('float32')
    kpts = bigMapDataArray[:,:7]
    desc = bigMapDataArray[:,7:]
    des2 = np.array(desc)
    kp2 = [cv2.KeyPoint(x, y, _size, _angle, _response, int(_octave), int(_class_id))
                     for x, y, _size, _angle, _response, _octave, _class_id in list(kpts)]
    #Load all mini map images into an array
    for file in glob.glob(mapFolderPath+ '/*.png'):
        miniMapNumber=1+miniMapNumber
        all_images.append(cv2.imread(file))
    print('Number of mini-maps to match ' +str(miniMapNumber))
    lastPoint = []  
    plt.axis('off')
    dst_line_final = []
    loopNumber = 0
    #set all valid sizes of polygonal homography matches
    polysizeArray = [650000,650000,560000,340000,540000,440000,600000]
    print('Starting matching')
    for file in tqdm(glob.glob(mapFolderPath+ '/*.png')):
        loopNumber = loopNumber + 1
        picNumber = picNumber + 1
        goodMatches = []
        img1 = all_images[loopNumber-1]
        #compute descriptors and key points on the mini map images 
        kp1, des1 = featureMappingAlgMiniMap.detectAndCompute(img1,None)
        matches = featureMatcher.knnMatch(des1,des2,k=2)
        #Use the ratio test to find good matches
        for m,n in matches:  
            if m.distance < 0.65*n.distance:
                goodMatches.append(m)    
        if len(goodMatches)>=MIN_MATCH_COUNT:
            #Find homography 
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in goodMatches]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in goodMatches]).reshape(-1,1,2)
            M, _ = cv.findHomography(src_pts,dst_pts, cv.RANSAC,5.0)
            h,w,_= img1.shape
            #create a rectangle around the matching area
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            if M is None:
                continue
            #Perform a homographic perspective transform on the rectangle of points in order to map the sub image to the main image 
            dst = cv.perspectiveTransform(pts,M)
            #Calculate the size of the newly transformed polygon
            polySize =  np.int_(cv.contourArea(dst))
            #Use a rolling average to avoid hard coding size restrictions 
            rolling_avg = int((np.sum(polysizeArray[-4:-1])/3))
            polysizeArray.append(polySize)
            if polySize > int(rolling_avg*2) or polySize < int(rolling_avg*0.5):
                continue
            print('Found match for file ' + str(file) +' [Matches: ' +str(len(goodMatches)) +'] [Polygonal size: ' +str(polySize)+']')
            #Perform another perspective transform on a dot in the middle of the polygon to find it's center point
            dst_dot = cv.perspectiveTransform(np.float32((115,86)).reshape(-1,1,2),M)
            if len(dst_line_final) == 0:
                dst_line_final = dst_dot.copy()
            if len(lastPoint) == 0:
                lastPoint = dst_dot.copy()
                continue
            color = (225, 0, 255)
            #Combine all found center coordinates  
            dst_line_final =  np.concatenate([dst_dot,dst_line_final])
            imageNumber.append(loopNumber-1)
            foundData.append(np.int32(dst_dot)[0][0])
            thickness = 1
            matchNumber= matchNumber + 1
            #Queue image to be sent to the live image preview window 
            image1 = cv.polylines(editedImage,[np.int32(dst_line_final)],False,color,2, cv.LINE_AA)
            queuedImage.put(image1)
            lastPoint = dst_dot.copy()
        else:
            print('Not enough matches for file ' + str(file) +' ' +' [Matches: ' +str(len(goodMatches)) +']')
    #Save all found center points
    save(foundData, imageNumber)
    finalOutputBase = cv2.imread(map)
    #Draw all the center points with lines connecting them on the main image 
    finalOutputBase = cv.polylines(finalOutputBase,[np.int32(dst_line_final)],False,color,thickness, cv.LINE_AA)
    finalOutputBase = cv2.cvtColor(finalOutputBase, cv2.COLOR_BGR2RGB)
    plt.imsave(outputMapPath + str(picNumber) +'_FINAL' +'.png', finalOutputBase)


def save(foundData, imageNumber):
    x,y = np.split(np.asarray(foundData),2,axis=1)
    print(np.asarray(foundData))
    x = [item for sublist in x for item in sublist]
    y = [item for sublist in y for item in sublist]
    np.save('outputdata/miniMapData.npy', np.vstack((x,y, imageNumber)))
    print('Save successful')


def display(queuedImage):
    cv2.namedWindow('mapImage', cv2.WINDOW_NORMAL)
    cv2.imshow("mapImage",cv2.imread(gameMap))
    while True:
        if not queuedImage.empty():
            imS = cv2.resize(queuedImage.get(), (1333,1000)) 
            cv2.imshow("mapImage",imS)
            
            continue
        cv2.waitKey(1) 

if __name__ == '__main__':
    print('Starting MiniMap Matching')
    queuedImage = multiprocessing.Queue()
    process1 = multiprocessing.Process(target=miniMapPlotter, args=(queuedImage,))
    process2 = multiprocessing.Process(target=display, args=(queuedImage,))
    process1.start()
    process2.start()