"""
    retrieve_controller.create_logs_directory(study)
    retrieve_controller.extract_result(study)

    The remaining missing methods are not tested here, because already done in RetrieveController unit tests.
"""

from unittest import mock

from antareslauncher.remote_environnement.remote_environment_with_slurm import (
    RemoteEnvironmentWithSlurm,
)
from antareslauncher.remote_environnement.slurm_script_features import (
    SlurmScriptFeatures,
)
from antareslauncher.use_cases.retrieve.retrieve_controller import RetrieveController
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater


class TestIntegrationRetrieveController:
    def setup_method(self):
        connection = mock.Mock()
        connection.home_dir = "Submitted"
        slurm_script_features = SlurmScriptFeatures(definitions.SLURM_SCRIPT_PATH)
        self.env = RemoteEnvironmentWithSlurm(
            _connection=connection, slurm_script_features=slurm_script_features
        )
        state_updater = StateUpdater(env=self.env, display=mock.Mock())
        self.retrieve_controller = RetrieveController(
            repo=mock.Mock(),
            env=self.env,
            file_manager=mock.Mock(),
            display=mock.Mock(),
            state_updater=state_updater,
        )
