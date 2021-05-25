from unittest import mock

import pytest

from antareslauncher.remote_environnement.remote_environment_with_slurm import (
    RemoteEnvironmentWithSlurm,
)
from antareslauncher.remote_environnement.slurm_script_features import (
    SlurmScriptFeatures,
)
from antareslauncher.use_cases.kill_job.job_kill_controller import (
    JobKillController,
)


class TestIntegrationJobKilController:
    def setup_method(self):
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        env = RemoteEnvironmentWithSlurm(mock.Mock(), slurm_script_features)
        self.job_kill_controller = JobKillController(env, mock.Mock(), repo=mock.Mock())

    @pytest.mark.integration_test
    def test_job_kill_controller_kill_job_calls_connection_execute_command(
        self,
    ):
        # given
        job_id = 42
        self.job_kill_controller.env.connection.execute_command = mock.Mock(
            return_value=("", "")
        )
        # when
        self.job_kill_controller.kill_job(job_id)
        # then
        self.job_kill_controller.env.connection.execute_command.assert_called_once_with(
            f"scancel {job_id}"
        )
