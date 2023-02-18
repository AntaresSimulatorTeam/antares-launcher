from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.use_cases.create_list.study_list_composer import (
    StudyListComposer,
    StudyListComposerParameters,
)


class TestIntegrationStudyListComposer:
    def setup_method(self):
        self.study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=mock.Mock(),
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
    def test_study_list_composer_get_list_of_studies_calls_repo_get_list_of_studies(
        self,
    ):
        self.study_list_composer.get_list_of_studies()
        self.study_list_composer._repo.get_list_of_studies.assert_called_once()

    @pytest.mark.integration_test
    def test_study_list_composer_get_antares_version_calls_file_manager_get_config_from_file(
        self,
    ):
        # given
        directory_path = "directory_path"
        file_path = Path(directory_path) / "study.antares"
        self.study_list_composer._file_manager.get_config_from_file = mock.Mock(
            return_value={}
        )
        # when
        self.study_list_composer.get_antares_version(directory_path)
        # then
        self.study_list_composer._file_manager.get_config_from_file.assert_called_once_with(
            file_path
        )

    # TODO: test_update_study_database already in unit tests?
