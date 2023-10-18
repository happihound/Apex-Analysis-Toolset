import numpy as np
import cv2
import sys
import os


def validate_input(gameMap, ratio):
    valid_maps = ['KC', 'WE', 'OLY', 'SP', 'BM']
    valid_ratios = ['4by3', '16by9', '16by10']
    if gameMap not in valid_maps or ratio not in valid_ratios:
        print('Invalid map name or aspect ratio. Please, enter valid ones.')
        print("\tValid map names: 'KC', 'WE', 'OLY', 'SP', 'BM'")
        print("\tValid ratios: '4by3', '16by9', '16by10'")
        exit()


def packKeyPoints(ratio, gameMap):
    validate_input(gameMap, ratio)
    # Test if the file already exists
    keypointPath = f'internal/packedKeypoints/{ratio}/{gameMap}{ratio}KeyPoints.npy'
    if os.path.isfile(keypointPath):
        print('Map data already exists')
        return
    print(f'Packing Keypoints for {gameMap} {ratio} map')
    editedImage = cv2.imread(f'internal/maps/{ratio}/map{gameMap}{ratio}.jpg')

    featureMappingAlg = cv2.SIFT_create(nOctaveLayers=35, nfeatures=250000)
    kp1, des1 = featureMappingAlg.detectAndCompute(editedImage, None)

    kpts = np.array([[kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id] for kp in kp1])
    desc = np.array(des1)

    print(f'Saving\nNumber of keypoints: {len(kp1)}')

    np.save(f'internal/packedKeypoints/{ratio}/{gameMap}{ratio}KeyPoints.npy', np.hstack((kpts, desc)))


def process_args(args):
    if "debug" in args or False:
        print("Debug mode")
        packKeyPoints('4by3', 'KC')

    if len(args) == 1:
        print("Command format:")
        print("\tmapDataPacker.py -mapName=MAPNAME -ratio=RATIO")
    else:
        ratio, gameMap = args[1].split('=')[1], args[0].split('=')[1]
        packKeyPoints(ratio, gameMap)


if __name__ == '__main__':
    print('Starting MiniMap Packing Tool')
    process_args(sys.argv)
