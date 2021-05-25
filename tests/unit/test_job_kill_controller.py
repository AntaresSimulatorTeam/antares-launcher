from unittest import mock

import pytest

from antareslauncher.use_cases.kill_job.job_kill_controller import (
    JobKillController,
)


class TestJobKillController:
    @pytest.mark.unit_test
    def test_job_kill_controller_should_display_message_when_it_kills_a_job(
        self,
    ):
        # given
        job_kill_controller = JobKillController(
            env=mock.Mock(),
            display=mock.Mock(),
            repo=mock.Mock(),
        )
        # when
        job_kill_controller.kill_job(42)
        # then
        job_kill_controller.display.show_message.assert_called_once()

    @pytest.mark.unit_test
    def test_job_kill_controller_should_call_env_kill_remote_job(self):
        # given
        job_kill_controller = JobKillController(
            env=mock.Mock(),
            display=mock.Mock(),
            repo=mock.Mock(),
        )
        # when
        job_id = 42
        job_kill_controller.kill_job(job_id)
        # then
        job_kill_controller.env.kill_remote_job.assert_called_once_with(job_id)
