from unittest import mock

import pytest

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.final_zip_extractor import (
    FinalZipExtractor,
    ResultNotExtractedException,
)


class TestFinalZipExtractor:
    def setup_method(self):
        self.file_manager = mock.Mock(spec_set=FileManager)
        self.display_mock = mock.Mock(spec_set=IDisplay)
        self.zip_extractor = FinalZipExtractor(self.file_manager, self.display_mock)

    @pytest.fixture(scope="function")
    def study_to_extract(self):
        local_zip = "results.zip"
        study = StudyDTO(
            path="hello",
            local_final_zipfile_path=local_zip,
            final_zip_extracted=False,
        )
        return study

    @pytest.mark.unit_test
    def test_extract_zip_show_message_if_zip_succeeds(self, study_to_extract):
        self.file_manager.unzip = mock.Mock(return_value=True)

        self.zip_extractor.extract_final_zip(study_to_extract)

        expected_message = f'"hello": Final zip extracted'
        self.display_mock.show_message.assert_called_once_with(
            expected_message, mock.ANY
        )

    @pytest.mark.unit_test
    def test_extract_zip_show_error_and_raises_exception_if_zip_fails(
        self, study_to_extract
    ):
        self.file_manager.unzip = mock.Mock(return_value=False)

        with pytest.raises(ResultNotExtractedException):
            self.zip_extractor.extract_final_zip(study_to_extract)

        expected_error = f'"hello": Final zip not extracted'
        self.display_mock.show_error.assert_called_once_with(expected_error, mock.ANY)

    @pytest.mark.unit_test
    def test_file_manager_not_called_if_study_should_not_be_extracted(self):
        self.file_manager.unzip = mock.Mock()
        empty_study = StudyDTO("hello")

        new_study = self.zip_extractor.extract_final_zip(empty_study)
        self.file_manager.unzip.assert_not_called()
        self.display_mock.show_error.assert_not_called()
        self.display_mock.show_message.assert_not_called()
        assert new_study == empty_study

    @pytest.mark.unit_test
    def test_file_manager_is_called_if_study_is_ready(self, study_to_extract):
        self.file_manager.unzip = mock.Mock(return_value=True)

        new_study = self.zip_extractor.extract_final_zip(study_to_extract)
        self.file_manager.unzip.assert_called_once_with(
            study_to_extract.local_final_zipfile_path
        )
        assert new_study.final_zip_extracted is True
