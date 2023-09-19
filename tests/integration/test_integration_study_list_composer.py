from unittest import mock

import pytest
from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.use_cases.create_list.study_list_composer import (
    StudyListComposer,
    StudyListComposerParameters,
)


class TestIntegrationStudyListComposer:
    def setup_method(self):
        self.repo = mock.Mock(spec=DataRepoTinydb)
        self.file_manager = mock.Mock(spec=FileManager)
        self.display = mock.Mock(spec=DisplayTerminal)
        self.study_list_composer = StudyListComposer(
            repo=self.repo,
            file_manager=self.file_manager,
            display=self.display,
            parameters=StudyListComposerParameters(
                studies_in_dir="studies_in",
                time_limit=42,
                n_cpu=24,
                log_dir="job_log_dir",
                xpansion_mode=None,
                output_dir="output_dir",
                post_processing=False,
                antares_versions_on_remote_server=["700"],
                other_options="",
            ),
        )

    @pytest.mark.integration_test
    def test_get_list_of_studies(self):
        self.study_list_composer.get_list_of_studies()
        self.repo.get_list_of_studies.assert_called_once_with()

    @pytest.mark.integration_test
    def test_update_study_database(self):
        self.file_manager.listdir_of = mock.Mock(return_value=["study1", "study2"])
        self.file_manager.is_dir = mock.Mock(return_value=True)
        self.study_list_composer.xpansion_mode = "r"  # "r", "cpp" or None
        self.study_list_composer.update_study_database()
        self.display.show_message.assert_called()
