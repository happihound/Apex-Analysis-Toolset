import pytest
import multiprocessing
import os
import csv
from unittest.mock import patch, Mock
from ApexUtils import ApexUtils


def test_display_starts_process():
    utils = ApexUtils()
    queue = multiprocessing.Queue()
    end = multiprocessing.Value('i', 0)
    window_name = "Test Window"

    with patch("multiprocessing.Process.start") as mock_start:
        utils.display(queue, end, window_name)
        mock_start.assert_called()


def test_save_file_exists():
    delete_test_files()
    utils = ApexUtils()
    data = ["Hello", "World"]
    frame = [1, 2]
    headers = ["Header1", "Header2"]
    filename = "existing_file"

    # Create a dummy file to trigger FileExistsError
    with open(f'outputdata/test_{filename}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerow([frame[0], data[0]])

    with pytest.raises(FileExistsError):
        utils.save(data, frame, headers, filename, debug=True)


def test_save_no_data():
    delete_test_files()
    utils = ApexUtils()
    data = None
    frame = None

    with pytest.raises(Exception):
        utils.save(data, frame)


def test_save_no_name():
    delete_test_files()
    utils = ApexUtils()
    data = ["Hello", "World"]
    frame = [1, 2]
    headers = ["Header1", "Header2"]

    with patch('builtins.print') as mock_print:
        utils.save(data, frame, headers, debug=True)
        assert os.path.exists("outputdata/test_default.csv")


def test_save_file_not_found():
    delete_test_files()
    utils = ApexUtils()
    data = ["Hello", "World"]
    frame = [1, 2]
    headers = ["Header1", "Header2"]
    filename = "/non_existing_dir/test"

    with pytest.raises(FileNotFoundError):
        utils.save(data, frame, headers, filename, debug=True)


def delete_test_files():
    # Delete all files created by tests
    for file in os.listdir("outputdata"):
        if file.startswith("test_"):
            os.remove(f"outputdata/{file}")
