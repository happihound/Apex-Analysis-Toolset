import pytest
import cv2
import glob
import multiprocessing
import ApexUtils
import easyocr
import evoTracker

# Mock objects


@pytest.fixture
def mock_ocr(monkeypatch):
    class MockOCR:
        def __init__(self, lang):
            self.lang = lang

        def readtext(self, image, allowlist=None, paragraph=False):
            return [(None, '123', 0.94)]
    monkeypatch.setattr(easyocr, 'Reader', MockOCR)


@pytest.fixture
def mock_apex_utils(monkeypatch):
    class MockApexUtils:
        def __init__(self):
            pass

        def save(self, data, frame, headers, name):
            pass

        def display(self, queue, end, name):
            pass

    monkeypatch.setattr(ApexUtils, 'ApexUtils', MockApexUtils)


@pytest.fixture
def mock_cv2(monkeypatch):
    def mock_imread(file):
        return 'test_image'

    monkeypatch.setattr(cv2, 'imread', mock_imread)


@pytest.fixture
def mock_glob(monkeypatch):
    def mock_glob(path):
        return ['image1.png', 'image2.png', 'image3.png']

    monkeypatch.setattr(glob, 'glob', mock_glob)


def test_process_result(mock_ocr):
    evo_tracker = evoTracker.evoTracker()
    evo_tracker.reader = easyocr.Reader(['en'])
    result = evo_tracker.process_result([(None, '123', 0.94)], None)
    assert result == True
    assert evo_tracker.results == [0, 123]
    assert evo_tracker.match_count == 1


def test_is_valid_evo():
    evo_tracker = evoTracker.evoTracker()
    assert evo_tracker.is_valid_evo(751) == False
    assert evo_tracker.is_valid_evo(-1) == False
    assert evo_tracker.is_valid_evo(0) == False
    assert evo_tracker.is_valid_evo(750) == True


def test_filter_Values():
    evo_tracker = evoTracker.evoTracker()
    evo_tracker.results = [0, 1, 2, 3, 4, 5, 6]
    evo_tracker.filter_Values(evo_tracker.results)
    assert evo_tracker.results == [0, 1, 2, 3, 4, 5, 6]
    assert evo_tracker.match_count == 7


def test_track_evo(mock_ocr, mock_apex_utils, mock_cv2, mock_glob):
    evo_tracker = evoTracker.evoTracker()
    end = multiprocessing.Value("i", False)
    queued_image = multiprocessing.Queue()
    evo_tracker.track_evo(queued_image, end)
    assert end.value == True
    assert evo_tracker.match_count == 4
    assert evo_tracker.results == [0, 123, 123, 123]
