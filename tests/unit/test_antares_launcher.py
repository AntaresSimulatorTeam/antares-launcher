from unittest import mock
from unittest.mock import PropertyMock, Mock

import pytest

from antareslauncher.antares_launcher import AntaresLauncher
from antareslauncher.use_cases.wait_loop_controller.wait_controller import (
    WaitController,
)


class TestAntaresLauncher:
    @pytest.mark.unit_test
    def test_given_job_id_to_kill_when_run_then_job_kill_controller_kills_job_with_good_id(
        self,
    ):
        # given
        job_id_to_kill = 42
        dummy = Mock()
        antares_launcher = AntaresLauncher(
            study_list_composer=dummy,
            launch_controller=dummy,
            retrieve_controller=dummy,
            job_kill_controller=mock.Mock(),
            check_queue_controller=dummy,
            wait_controller=dummy,
            wait_mode=False,
            wait_time=42,
            xpansion_mode=None,
            job_id_to_kill=job_id_to_kill,
            check_queue_bool=False,
        )
        # when
        antares_launcher.run()
        # then
        antares_launcher.job_kill_controller.kill_job.assert_called_once_with(
            job_id_to_kill
        )

    @pytest.mark.unit_test
    def test_given_true_check_queue_bool_when_run_then_check_queue_controller_checks_queue(
        self,
    ):
        # given
        dummy = Mock()
        antares_launcher = AntaresLauncher(
            study_list_composer=dummy,
            launch_controller=dummy,
            retrieve_controller=dummy,
            job_kill_controller=dummy,
            check_queue_controller=Mock(),
            wait_controller=dummy,
            wait_mode=False,
            wait_time=42,
            xpansion_mode=None,
            check_queue_bool=True,
        )
        # when
        antares_launcher.run()
        # then
        antares_launcher.check_queue_controller.check_queue.assert_called_once()

    @pytest.mark.unit_test
    def test_given_true_wait_mode_when_run_then_run_wait_mode_called(self):
        # given
        antares_launcher = AntaresLauncher(
            study_list_composer=None,
            launch_controller=None,
            retrieve_controller=None,
            job_kill_controller=None,
            check_queue_controller=None,
            wait_controller=None,
            wait_mode=True,
            wait_time=None,
            xpansion_mode=None,
            job_id_to_kill=None,
            check_queue_bool=None,
        )
        antares_launcher.run_wait_mode = mock.Mock()
        # when
        antares_launcher.run()
        # then
        antares_launcher.run_wait_mode.assert_called_once()

    @pytest.mark.unit_test
    def test_given_false_wait_mode_when_run_then_run_once_mode_called(self):
        # given
        antares_launcher = AntaresLauncher(
            study_list_composer=None,
            launch_controller=None,
            retrieve_controller=None,
            job_kill_controller=None,
            check_queue_controller=None,
            wait_controller=None,
            wait_mode=False,
            wait_time=None,
            xpansion_mode=None,
            job_id_to_kill=None,
            check_queue_bool=None,
        )
        antares_launcher.run_once_mode = mock.Mock()
        # when
        antares_launcher.run()
        # then
        antares_launcher.run_once_mode.assert_called_once()

    @pytest.mark.unit_test
    def test_given_true_run_wait_mode_when_all_studies_done_the_third_time_then_retrieve_all_studies_is_called_three_times(
        self,
    ):
        # given
        wait_controller = WaitController(display=mock.Mock())
        wait_controller.countdown = mock.Mock()
        antares_launcher = AntaresLauncher(
            study_list_composer=mock.Mock(),
            launch_controller=mock.Mock(),
            retrieve_controller=mock.Mock(),
            job_kill_controller=None,
            check_queue_controller=None,
            wait_controller=wait_controller,
            wait_mode=True,
            wait_time=1,
            xpansion_mode=None,
            job_id_to_kill=None,
            check_queue_bool=None,
        )
        type(antares_launcher.retrieve_controller).all_studies_done = PropertyMock(
            side_effect=[False, False, True, False]
        )
        # when
        antares_launcher.run()
        # then
        assert antares_launcher.retrieve_controller.retrieve_all_studies.call_count == 3
        assert wait_controller.countdown.call_count == 2
