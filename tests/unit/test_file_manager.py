import os
import shutil
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.file_manager import file_manager
from antareslauncher.study_dto import StudyDTO
from tests.data import DATA_DIR

DIR_TO_ZIP = DATA_DIR / "file-manager-test" / "to-zip"
DIR_REF = DATA_DIR / "file-manager-test" / "reference-without-output" / "to-zip"


def get_dict_from_path(path: Path):
    if os.path.isdir(path):
        return {
            "name": path.name,
            "type": "directory",
            "children": list(map(get_dict_from_path, path.iterdir())),
        }
    else:
        return {
            "name": path.name,
            "type": "file",
        }


class TestFileManager:
    @pytest.mark.unit_test
    def test_golden_master_for_zip_study_excluding_output_dir(self, tmp_path):
        dir_to_zip = DIR_TO_ZIP
        zip_name = str(dir_to_zip) + ".zip"
        display_terminal = DisplayTerminal()
        my_file_manager = file_manager.FileManager(display_terminal)

        my_file_manager.zip_dir_excluding_subdir(dir_to_zip, zip_name, "output")

        shutil.unpack_archive(zip_name, tmp_path)
        results = tmp_path / dir_to_zip.name
        results_dict = get_dict_from_path(results)
        reference_dict = get_dict_from_path(DIR_REF)

        assert results_dict == reference_dict
        result_zip_file = Path(zip_name)
        assert result_zip_file.is_file()
        result_zip_file.unlink()

    @pytest.mark.unit_test
    def test_unzip(self):
        """
        Tests the scenario where the specified zip file does not exist. The expected outcome is
        that the function returns False, indicating that the zip file could not be unzipped.
        This test is checking that the function correctly handles the case where the input file is not present.
        """
        # given
        study = StudyDTO("path")
        display_terminal = DisplayTerminal()
        my_file_manager = file_manager.FileManager(display_terminal)
        # when
        output = my_file_manager.unzip(study.local_final_zipfile_path)
        # then
        assert output is False

    @pytest.mark.unit_test
    def test__get_list_dir_without_subdir(self):
        """
        Tests the case where a directory path and a subdirectory name are given as inputs to the function.
        The function is expected to return a list of items in the directory, excluding the specified subdirectory.
        """
        # given
        display_terminal = DisplayTerminal()
        my_file_manager = file_manager.FileManager(display_terminal)
        listdir = ["dir1", "dir2", "dir42"]
        my_file_manager.listdir_of = mock.Mock(return_value=listdir.copy())
        subdir_to_exclude = "dir42"
        listdir.remove(subdir_to_exclude)
        # when
        output = my_file_manager._get_list_dir_without_subdir("", subdir_to_exclude)
        # then
        assert listdir == output
