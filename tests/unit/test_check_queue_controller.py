from unittest import mock

import pytest

from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.check_remote_queue.check_queue_controller import (
    CheckQueueController,
)
from antareslauncher.use_cases.check_remote_queue.slurm_queue_show import (
    SlurmQueueShow,
)
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater


class TestCheckQueueController:
    def setup_method(self):
        self.repo_mock = mock.Mock(spec=IDataRepo)
        self.env = mock.Mock()
        self.display = mock.Mock()
        self.slurm_queue_show = SlurmQueueShow(env=self.env, display=self.display)
        self.state_updater = StateUpdater(env=mock.Mock(), display=self.display)
        self.check_queue_controller = CheckQueueController(
            slurm_queue_show=self.slurm_queue_show,
            state_updater=self.state_updater,
            repo=self.repo_mock,
        )

    @pytest.mark.unit_test
    def test_check_queue_controller_calls_slurm_queue_show_once(self):
        # given
        self.slurm_queue_show.run = mock.Mock()
        self.repo_mock.get_list_of_studies = (
            mock.MagicMock()
        )  # mock.Mock(return_value=[])
        # when
        self.check_queue_controller.check_queue()
        # then
        self.slurm_queue_show.run.assert_called_once()

    @pytest.mark.unit_test
    def test_when_check_queue_controller_runs_repo_get_list_is_called(self):
        # given
        self.slurm_queue_show.run = mock.Mock()
        self.repo_mock.get_list_of_studies = mock.MagicMock()
        # when
        self.check_queue_controller.check_queue()
        # then
        self.repo_mock.get_list_of_studies.assert_called_once()

    @pytest.mark.unit_test
    def test_given_one_study_in_repo_check_queue_controller_calls_updater_once_with_study(
        self,
    ):
        # given
        study = StudyDTO("")
        self.slurm_queue_show.run = mock.Mock()
        self.repo_mock.get_list_of_studies = mock.Mock(return_value=[study])
        self.state_updater.run = mock.Mock()
        # when
        self.check_queue_controller.check_queue()
        # then
        self.state_updater.run.assert_called_once_with(study)

    @pytest.mark.unit_test
    def test_check_queue_controller_writes_message_before_returning_state_of_studies(
        self,
    ):
        # given
        study_list = [StudyDTO(""), StudyDTO("")]
        self.slurm_queue_show.run = mock.Mock()
        self.repo_mock.get_list_of_studies = mock.Mock(return_value=study_list)
        self.state_updater.run_on_list = mock.Mock()
        self.display.show_message = mock.Mock()
        # when
        self.check_queue_controller.check_queue()
        # then
        self.state_updater.run_on_list.assert_called_once_with(study_list)

    @pytest.mark.unit_test
    def test_given_two_studies_in_repo_check_queue_controller_calls_updater_twice(
        self,
    ):
        # given
        study_list = [StudyDTO(""), StudyDTO("")]
        self.slurm_queue_show.run = mock.Mock()
        self.state_updater.run = mock.Mock()
        self.repo_mock.get_list_of_studies = mock.Mock(return_value=study_list)
        self.display.show_message = mock.Mock()
        # when
        self.check_queue_controller.check_queue()
        # then
        assert self.state_updater.run.call_count == 2
