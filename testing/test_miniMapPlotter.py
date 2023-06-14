import pytest
import numpy as np
import cv2 as cv

from miniMapPlotter import miniMapPlotter


def test_setMap():
    minimap = miniMapPlotter()
    minimap.setMap("KC")
    assert minimap.map == "KC"


def test_setRatio():
    minimap = miniMapPlotter()
    minimap.setRatio("4by3")
    assert minimap.ratio == "4by3"

# need to add more tests, but this is good enough for now
