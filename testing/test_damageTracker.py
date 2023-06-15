import pytest
import cv2
from unittest.mock import MagicMock, patch
from multiprocessing import Queue, Value

import damageTracker  # Replace 'your_module' with the module of your class.

# Prepare the fixture for DamageTracker


@pytest.fixture
def tracker():
    tracker = damageTracker.DamageTracker()
    return tracker


def test_process_result(tracker):
    bbox, text, prob = ((0, 0), (0, 0)), "200", 0.94
    result_OCR = [(bbox, text, prob)]
    pbar = MagicMock()
    tracker.results = [150]  # Set some initial damage

    assert tracker.process_result(result_OCR, pbar) is True
    assert tracker.match_count == 1
    assert tracker.results == [150, 200]


def test_is_valid_damage(tracker):
    pbar = MagicMock()
    tracker.results = [100]

    assert tracker.is_valid_damage(150, pbar) is True
    assert tracker.is_valid_damage(90, pbar) is False
