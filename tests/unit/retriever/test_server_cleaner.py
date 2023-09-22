from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.clean_remote_server import RemoteServerCleaner


class TestServerCleaner:
    @pytest.mark.unit_test
    def test_clean__finished_study__nominal(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.clean_remote_server.return_value = True
        display = mock.Mock(spec=DisplayTerminal)

        # Prepare a fake
        finished_study.local_final_zipfile_path = "/path/to/result.zip"

        # Initialize and execute the cleaning
        cleaner = RemoteServerCleaner(env, display)
        cleaner.clean(finished_study)

        # Check the result
        env.clean_remote_server.assert_called_once()
        display.show_message.assert_called()
        display.show_error.assert_not_called()

        assert finished_study.remote_server_is_clean

    @pytest.mark.unit_test
    def test_clean__finished_study__no_result(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.clean_remote_server.return_value = True
        display = mock.Mock(spec=DisplayTerminal)

        # Prepare a fake
        finished_study.local_final_zipfile_path = ""

        # Initialize and execute the cleaning
        cleaner = RemoteServerCleaner(env, display)
        cleaner.clean(finished_study)

        # Check the result
        env.clean_remote_server.assert_not_called()
        display.show_message.assert_not_called()
        display.show_error.assert_not_called()

        assert not finished_study.remote_server_is_clean

    @pytest.mark.unit_test
    def test_clean__finished_study__reentrancy(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.clean_remote_server.return_value = True
        display = mock.Mock(spec=DisplayTerminal)

        # Prepare a fake
        finished_study.local_final_zipfile_path = "/path/to/result.zip"

        # Initialize and execute the cleaning twice
        cleaner = RemoteServerCleaner(env, display)
        cleaner.clean(finished_study)
        cleaner.clean(finished_study)

        # Check the result
        env.clean_remote_server.assert_called_once()
        display.show_message.assert_called()
        display.show_error.assert_not_called()

        assert finished_study.remote_server_is_clean

    @pytest.mark.unit_test
    def test_clean__finished_study__cleaning_failed(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.clean_remote_server.return_value = False
        display = mock.Mock(spec=DisplayTerminal)

        # Prepare a fake
        finished_study.local_final_zipfile_path = "/path/to/result.zip"

        # Initialize and execute the cleaning
        cleaner = RemoteServerCleaner(env, display)
        cleaner.clean(finished_study)

        # Check the result
        env.clean_remote_server.assert_called_once()
        display.show_message.assert_not_called()
        display.show_error.assert_called()

        assert finished_study.remote_server_is_clean

    @pytest.mark.unit_test
    def test_clean__finished_study__cleaning_raise(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.clean_remote_server.side_effect = Exception("cleaning error")
        display = mock.Mock(spec=DisplayTerminal)

        # Prepare a fake
        finished_study.local_final_zipfile_path = "/path/to/result.zip"

        # Initialize and execute the cleaning
        cleaner = RemoteServerCleaner(env, display)
        cleaner.clean(finished_study)

        # Check the result
        env.clean_remote_server.assert_called_once()
        display.show_message.assert_not_called()
        display.show_error.assert_called()

        assert finished_study.remote_server_is_clean
