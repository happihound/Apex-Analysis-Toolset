import os
import cv2
import numpy as np
import mapDataPacker
import pytest


def loadMapKeyPoints(keypointPath):
    # Check if the file exists
    if not os.path.isfile(keypointPath):
        return False
    # Load baked key points
    print('Loading Map Data')
    # Load the packed numpy file
    mapKeyPoints = np.load(keypointPath).astype('float32')
    if len(mapKeyPoints) == 0:
        return False
    # Split the key points into their respective arrays
    tempKeyPoints = mapKeyPoints[:, :7]
    if len(tempKeyPoints) == 0:
        return False
    descriptors = np.array(mapKeyPoints[:, 7:])
    if len(descriptors) == 0:
        return False
    # Create a list of key points
    return True


resolutions = ['4by3', '16by9', '16by10']
tags = ['KC', 'WE', 'OLY', 'SP', 'BM']


@pytest.mark.parametrize('resolution,tag', [(r, t) for r in resolutions for t in tags])
def test_pack(resolution, tag):
    print(f'Packing Keypoints for {tag} {resolution} map')
    mapDataPacker.packKeyPoints(resolution, tag)
    assert loadMapKeyPoints(f'internal/packedKeypoints/{resolution}/{tag}{resolution}KeyPoints.npy')
