import os
import shutil
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.file_manager import file_manager
from antareslauncher.study_dto import StudyDTO

DATA_4_TEST_DIR = Path(__file__).parent.parent / "data" / "file-manager-test"

DIR_TO_ZIP = DATA_4_TEST_DIR / "to-zip"
DIR_REF = DATA_4_TEST_DIR / "reference-without-output" / "to-zip"


def get_dict_from_path(path):
    d = {"name": os.path.basename(path)}
    if os.path.isdir(path):
        d["type"] = "directory"
        d["children"] = [
            get_dict_from_path(os.path.join(path, x)) for x in os.listdir(path)
        ]
    else:
        d["type"] = "file"
    return d


class TestFileManager:
    @pytest.mark.unit_test
    def test_golden_master_for_zip_study_excluding_output_dir(self):
        dir_to_zip = DIR_TO_ZIP
        zip_name = str(dir_to_zip) + ".zip"
        display_terminal = DisplayTerminal()
        my_file_manager = file_manager.FileManager(display_terminal)

        my_file_manager.zip_dir_excluding_subdir(dir_to_zip, zip_name, "output")

        destination = DATA_4_TEST_DIR / "TMP"
        shutil.unpack_archive(zip_name, destination)
        results = destination / dir_to_zip.name
        results_dict = get_dict_from_path(results)
        reference_dict = get_dict_from_path(DIR_REF)

        assert results_dict == reference_dict
        result_zip_file = Path(zip_name)
        assert result_zip_file.is_file()
        result_zip_file.unlink()
        shutil.rmtree(destination)

    @pytest.mark.unit_test
    def test_if_zipfile_does_not_exist_then_unzip_returns_false(
        self,
    ):
        # given
        study = StudyDTO("path")
        display_terminal = DisplayTerminal()
        my_file_manager = file_manager.FileManager(display_terminal)
        # when
        output = my_file_manager.unzip(study.local_final_zipfile_path)
        # then
        assert output is False

    @pytest.mark.unit_test
    def test_given_dir_path_and_subdir_name_when_get_list_dir_without_subdir_called_return_listdir_without_subdir(
        self,
    ):
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
