from copy import deepcopy
from unittest import mock
from unittest.mock import call

import pytest

import antareslauncher
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.retrieve_controller import (
    RetrieveController,
)
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater


class TestRetrieveController:
    def setup_method(self):
        self.remote_env_mock = mock.Mock(spec=iremote_environment.IRemoteEnvironment)
        self.file_manager = mock.Mock()
        self.data_repo = mock.Mock()
        self.display = mock.Mock()
        self.state_updater_mock = StateUpdater(self.remote_env_mock, self.display)

    @pytest.fixture(scope="function")
    def my_study(self):
        return antareslauncher.study_dto.StudyDTO("")

    @pytest.fixture(scope="function")
    def my_running_study(self):
        study = antareslauncher.study_dto.StudyDTO(
            job_id=42,
            started=True,
            finished=False,
            with_error=False,
            path="path",
        )
        return study

    @pytest.fixture(scope="function")
    def my_finished_study(self):
        study = antareslauncher.study_dto.StudyDTO(
            job_id=42,
            started=True,
            finished=True,
            with_error=False,
            path="path",
        )
        return study

    @pytest.fixture(scope="function")
    def my_downloaded_study(self):
        study = antareslauncher.study_dto.StudyDTO(
            job_id=42,
            started=True,
            finished=True,
            with_error=False,
            local_final_zipfile_path="local_final_zipfile_path",
            path="path",
        )
        return study

    @pytest.mark.unit_test
    def test_given_one_study_when_retrieve_all_studies_call_then_study_retriever_is_called_once(
        self, my_study
    ):
        # given
        list_of_studies = [my_study]
        self.data_repo.get_list_of_studies = mock.Mock(return_value=list_of_studies)
        my_retriever = RetrieveController(
            self.data_repo,
            self.remote_env_mock,
            self.file_manager,
            self.display,
            self.state_updater_mock,
        )
        my_retriever.study_retriever.retrieve = mock.Mock()
        self.display.show_message = mock.Mock()
        # when
        my_retriever.retrieve_all_studies()
        # then
        self.display.show_message.assert_called_once_with(
            "Retrieving all studies", mock.ANY
        )
        my_retriever.study_retriever.retrieve.assert_called_once_with(my_study)

    @pytest.mark.unit_test
    def test_given_a_list_of_done_studies_when_all_studies_done_called_then_return_true(
        self,
    ):
        # given
        study = StudyDTO("path")
        study.done = True
        study_list = [deepcopy(study), deepcopy(study)]
        my_retriever = RetrieveController(
            self.data_repo,
            self.remote_env_mock,
            self.file_manager,
            self.display,
            self.state_updater_mock,
        )
        my_retriever.repo.get_list_of_studies = mock.Mock(return_value=study_list)
        # when
        output = my_retriever.all_studies_done
        # then
        assert output is True

    @pytest.mark.unit_test
    def test_given_a_list_of_done_studies_when_retrieve_all_studies_called_then_message_is_shown(
        self,
    ):
        # given
        study = StudyDTO("path")
        study.done = True
        study_list = [deepcopy(study), deepcopy(study)]
        display_mock = mock.Mock(spec=IDisplay)
        my_retriever = RetrieveController(
            self.data_repo,
            self.remote_env_mock,
            self.file_manager,
            display_mock,
            self.state_updater_mock,
        )
        my_retriever.repo.get_list_of_studies = mock.Mock(return_value=study_list)
        display_mock.show_message = mock.Mock()
        # when
        output = my_retriever.retrieve_all_studies()
        # then
        expected_message1 = "Retrieving all studies"
        expected_message2 = "Everything is done"
        calls = [
            call(expected_message1, mock.ANY),
            call(expected_message2, mock.ANY),
        ]  # , call(my_study3)]
        display_mock.show_message.assert_has_calls(calls)
        assert output is True
