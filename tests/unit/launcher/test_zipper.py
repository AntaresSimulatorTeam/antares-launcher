import getpass
from unittest import mock

import pytest

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch.study_zipper import StudyZipper


class TestStudyZipper:
    def setup_method(self):
        self.file_manager = mock.Mock(spec_set=FileManager)
        self.display_mock = mock.Mock(spec_set=IDisplay)
        self.study_zipper = StudyZipper(self.file_manager, self.display_mock)

    @pytest.mark.unit_test
    def test_zip_study_show_message_if_zip_succeeds(self):
        self.file_manager.zip_dir_excluding_subdir = mock.Mock(return_value=True)
        study = StudyDTO(path="hello")

        self.study_zipper.zip(study)

        expected_message = f'"hello": was zipped'
        self.display_mock.show_message.assert_called_once_with(
            expected_message, mock.ANY
        )

    @pytest.mark.unit_test
    def test_zip_study_show_error_if_zip_fails(self):
        self.file_manager.zip_dir_excluding_subdir = mock.Mock(return_value=False)
        study = StudyDTO(path="hello")

        new_study = self.study_zipper.zip(study)

        expected_message = f'"hello": was not zipped'
        self.display_mock.show_error.assert_called_once_with(expected_message, mock.ANY)
        assert new_study.zipfile_path == ""

    @pytest.mark.unit_test
    def test_file_manager_not_called_if_zip_exists(self):
        self.file_manager.zip_dir_excluding_subdir = mock.Mock()
        study = StudyDTO(path="hello")
        study.zipfile_path = "ciao.zip"

        new_zip = self.study_zipper.zip(study)

        self.file_manager.zip_dir_excluding_subdir.assert_not_called()
        self.display_mock.show_error.assert_not_called()
        self.display_mock.show_message.assert_not_called()
        assert new_zip == study

    @pytest.mark.unit_test
    def test_file_manager_is_called_if_zip_doesnt_exist(self):
        self.file_manager.zip_dir_excluding_subdir = mock.Mock(return_value=True)
        study_path = "hello"
        study = StudyDTO(path=study_path)
        study.zipfile_path = ""

        new_study = self.study_zipper.zip(study)

        expected_zipfile_path = study.path + "-" + getpass.getuser() + ".zip"
        self.file_manager.zip_dir_excluding_subdir.assert_called_once_with(
            study_path, expected_zipfile_path, "output"
        )
        assert new_study.zipfile_path == expected_zipfile_path
