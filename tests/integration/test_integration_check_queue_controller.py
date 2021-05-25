from unittest import mock

import pytest

from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.remote_environnement.remote_environment_with_slurm import (
    RemoteEnvironmentWithSlurm,
)
from antareslauncher.remote_environnement.slurm_script_features import (
    SlurmScriptFeatures,
)
from antareslauncher.use_cases.check_remote_queue.check_queue_controller import (
    CheckQueueController,
)
from antareslauncher.use_cases.check_remote_queue.slurm_queue_show import (
    SlurmQueueShow,
)
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater


class TestIntegrationCheckQueueController:
    def setup_method(self):
        self.connection_mock = mock.Mock()
        self.connection_mock.username = "username"
        self.connection_mock.execute_command = mock.Mock(return_value=("", ""))
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        env_mock = RemoteEnvironmentWithSlurm(
            _connection=self.connection_mock,
            slurm_script_features=slurm_script_features,
        )
        display_mock = mock.Mock()
        slurm_queue_show = SlurmQueueShow(env_mock, display_mock)
        state_updater = StateUpdater(env_mock, display_mock)
        repo = mock.MagicMock(spec=IDataRepo)
        self.check_queue_controller = CheckQueueController(
            slurm_queue_show, state_updater, repo
        )

    @pytest.mark.integration_test
    def test_check_queue_controller_check_queue_calls_connection_execute_command(
        self,
    ):
        # when
        self.check_queue_controller.check_queue()
        # then
        self.connection_mock.execute_command.assert_called_once()
