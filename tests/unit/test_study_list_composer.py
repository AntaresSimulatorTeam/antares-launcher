from pathlib import Path
from unittest import mock
from unittest.mock import call

import pytest

from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.study_dto import Modes, StudyDTO
from antareslauncher.use_cases.create_list.study_list_composer import (
    StudyListComposer,
    StudyListComposerParameters,
)
from tests.data import DATA_DIR


class TestStudyListComposer:
    def setup_method(self):
        self.parameters = StudyListComposerParameters(
            studies_in_dir="",
            time_limit=0,
            n_cpu=1,
            log_dir="job_log_dir",
            xpansion_mode=None,
            output_dir="output_dir",
            post_processing=False,
            antares_versions_on_remote_server=["610", "700", "800"],
            other_options="",
        )

    @pytest.fixture(scope="function")
    def study_mock(self):
        study = mock.Mock()
        return study

    @pytest.mark.unit_test
    def test_given_repo_when_get_list_of_studies_called_then_repo_get_list_of_studies_is_called(
        self,
    ):

        # given
        repo_mock = mock.Mock()
        repo_mock.get_list_of_studies = mock.Mock()
        study_list_composer = StudyListComposer(
            repo=repo_mock,
            file_manager=None,
            display=None,
            parameters=self.parameters,
        )
        # when
        study_list_composer.get_list_of_studies()
        # then
        repo_mock.get_list_of_studies.assert_called_once()

    @pytest.mark.unit_test
    def test_given_repo_when_get_list_of_studies_called_then_repo_get_list_of_studies_is_called(
        self,
    ):
        # given

        repo_mock = mock.Mock()
        repo_mock.get_list_of_studies = mock.Mock()
        study_list_composer = StudyListComposer(
            repo=repo_mock,
            file_manager=None,
            display=None,
            parameters=self.parameters,
        )
        # when
        study_list_composer.get_list_of_studies()
        # then
        repo_mock.get_list_of_studies.assert_called_once()

    @pytest.mark.unit_test
    def test_when_is_dir_an_antares_study_is_called_then_the_file_study_antares_is_checked(
        self,
    ):
        # given

        dir_path = "dir_path"
        expected_config_file_path = Path(dir_path) / "study.antares"
        study_list_composer = StudyListComposer(
            repo=None,
            file_manager=mock.Mock(),
            display=None,
            parameters=self.parameters,
        )
        # when
        study_list_composer._file_manager.get_config_from_file = mock.Mock(
            return_value={}
        )
        return_value = study_list_composer.get_antares_version(dir_path)
        # then
        study_list_composer._file_manager.get_config_from_file.assert_called_once_with(
            expected_config_file_path
        )
        assert not return_value

    @pytest.mark.unit_test
    def test_when_antares_is_in_the_config_file_then_is_dir_an_antares_study_return_true(
        self,
    ):
        # given

        dir_path = "dir_path"
        expected_config_file_path = Path(dir_path) / "study.antares"
        study_list_composer = StudyListComposer(
            repo=None,
            file_manager=mock.Mock(),
            display=None,
            parameters=self.parameters,
        )
        # when
        study_list_composer._file_manager.get_config_from_file = mock.Mock(
            return_value={"antares": {"version": 42}}
        )
        return_value = study_list_composer.get_antares_version(dir_path)
        # then
        study_list_composer._file_manager.get_config_from_file.assert_called_once_with(
            expected_config_file_path
        )
        assert return_value

    @pytest.mark.unit_test
    def test_given_existing_db_when_no_new_study_then_do_nothing_and_show_message(
        self,
    ):
        # given
        self.parameters.studies_in_dir = "studies_in_dir"

        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(listdir_of=mock.Mock(return_value=["study"])),
            display=mock.Mock(),
            parameters=self.parameters,
        )
        study_list_composer.get_antares_version = mock.Mock(return_value=True)
        study_list_composer._repo.is_study_inside_database = mock.Mock(
            return_value=True
        )

        # when
        study_list_composer.update_study_database()

        # then
        assert study_list_composer._display.show_message.call_count == 3

    @pytest.mark.unit_test
    def test_given_existing_db_when_new_study_then_save_new_study_and_show_message(
        self,
    ):
        self.parameters.studies_in_dir = "studies_in_dir"
        self.parameters.time_limit = 24
        self.parameters.n_cpu = 42
        file_manager = mock.create_autospec(FileManager)
        file_manager.file_exists = mock.create_autospec(
            FileManager.file_exists, return_value=False
        )
        file_manager.listdir_of = mock.Mock(return_value=["study_path"])
        repo = mock.create_autospec(IDataRepo, instance=True)
        repo.is_study_inside_database = mock.Mock(return_value=False)
        # given
        study_list_composer = StudyListComposer(
            repo=repo,
            file_manager=file_manager,
            display=mock.Mock(),
            parameters=self.parameters,
        )
        study_list_composer.get_antares_version = mock.Mock(return_value="700")
        study_list_composer._file_manager.is_dir = mock.Mock(return_value=True)
        expected_save_study = StudyDTO(
            path=str(Path(self.parameters.studies_in_dir) / "study_path"),
            antares_version="700",
            job_log_dir=str(Path(self.parameters.log_dir) / "JOB_LOGS"),
            output_dir=self.parameters.output_dir,
            time_limit=self.parameters.time_limit,
            n_cpu=self.parameters.n_cpu,
            other_options="",
        )
        # when
        study_list_composer.update_study_database()

        # then
        calls = study_list_composer._repo.save_study.call_args_list
        assert calls[0] == call(expected_save_study)
        assert study_list_composer._display.show_message.call_count == 2

    @pytest.mark.unit_test
    def test_given_empty_study_dir_list_when_update_study_database_called_then_display_show_two_messages(
        self,
    ):
        # given
        study_list_composer = StudyListComposer(
            repo=None,
            file_manager=mock.Mock(listdir_of=mock.Mock(return_value=[])),
            display=mock.Mock(),
            parameters=self.parameters,
        )
        # when
        study_list_composer.update_study_database()
        # then
        assert study_list_composer._display.show_message.call_count == 2

    @pytest.mark.unit_test
    def test_given_two_new_studies_when_update_study_database_called_then_display_show_three_messages(
        self,
    ):
        # given
        self.parameters.studies_in_dir = "studies_in_dir"
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(
                listdir_of=mock.Mock(return_value=["study1", "study2"])
            ),
            display=mock.Mock(),
            parameters=self.parameters,
        )
        study_list_composer.get_antares_version = mock.Mock(return_value="700")
        study_list_composer._repo.is_study_inside_database = mock.Mock(
            return_value=False
        )
        study_list_composer._file_manager.is_dir = mock.Mock(return_value=True)
        # when
        study_list_composer.update_study_database()
        # then
        assert study_list_composer._display.show_message.call_count == 3

    @pytest.mark.unit_test
    def test_given_directory_path_when_create_study_is_called_then_return_study_dto_with_righ_values(
        self,
    ):
        # given
        self.parameters.studies_in_dir = "studies_in_dir"
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=mock.Mock(),
            parameters=self.parameters,
        )

        study_dir = study_list_composer._studies_in_dir
        antares_version = 700

        is_xpansion_study = None
        # when
        new_study_dto = study_list_composer._create_study(
            study_dir, antares_version, is_xpansion_study
        )
        # then
        assert new_study_dto.path == study_list_composer._studies_in_dir
        assert new_study_dto.n_cpu == study_list_composer.n_cpu
        assert new_study_dto.time_limit == study_list_composer.time_limit
        assert new_study_dto.antares_version == antares_version
        assert new_study_dto.job_log_dir == str(
            Path(study_list_composer.log_dir) / "JOB_LOGS"
        )

    @pytest.mark.unit_test
    def test_given_an_antares_version_when_is_valid_antares_study_is_called_return_boolean_value(
        self,
    ):
        # given
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=mock.Mock(),
            parameters=self.parameters,
        )
        antares_version_700 = "700"
        wrong_antares_version = "137"
        antares_version_none = None
        # when
        is_valid_antares_study_expected_true = (
            study_list_composer._is_valid_antares_study(antares_version_700)
        )
        is_valid_antares_study_expected_false = (
            study_list_composer._is_valid_antares_study(wrong_antares_version)
        )
        is_valid_antares_study_expected_false2 = (
            study_list_composer._is_valid_antares_study(antares_version_none)
        )
        # then
        assert is_valid_antares_study_expected_true is True
        assert is_valid_antares_study_expected_false is False
        assert is_valid_antares_study_expected_false2 is False

    @pytest.mark.unit_test
    def test_given_a_none_antares_version_when_is_antares_study_is_called_return_false_and_message(
        self,
    ):
        # given
        display_mock = mock.Mock()
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=display_mock,
            parameters=self.parameters,
        )
        display_mock.show_message = mock.Mock()
        antares_version = None
        # when
        is_antares_study = study_list_composer._is_valid_antares_study(antares_version)
        # then
        assert is_antares_study is False
        display_mock.show_message.assert_called_once_with(
            "... not a valid Antares study", mock.ANY
        )

    @pytest.mark.unit_test
    def test_given_a_non_supported_antares_version_when_is_antares_study_is_called_return_false_and_message(
        self,
    ):
        # given
        display_mock = mock.Mock()
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=display_mock,
            parameters=self.parameters,
        )
        display_mock.show_message = mock.Mock()
        antares_version = "600"
        message = f"... Antares version ({antares_version}) is not supported (supported versions: {self.parameters.antares_versions_on_remote_server})"
        # when
        is_antares_study = study_list_composer._is_valid_antares_study(antares_version)
        # then
        assert is_antares_study is False
        display_mock.show_message.assert_called_once_with(message, mock.ANY)

    @pytest.mark.unit_test
    def test_given_xpansion_study_path_when_is_xpansion_study_is_called_return_true(
        self,
    ):
        # given
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=mock.Mock(),
            parameters=self.parameters,
        )
        xpansion_study_path = Path("xpansion_study_path")
        study_list_composer._is_there_candidates_file = mock.Mock(return_value=True)
        # when
        is_xpansion_study = study_list_composer._is_xpansion_study(xpansion_study_path)
        # then
        assert is_xpansion_study is True

    @pytest.mark.unit_test
    def test_given_xpansion_study_path_when_create_study_is_called_then_xpansion_value_of_dto_is_true(
        self,
    ):
        # given
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=mock.Mock(),
            parameters=self.parameters,
        )

        study_dir = study_list_composer._studies_in_dir
        antares_version = 700

        is_xpansion_study = "r"
        # when
        new_study_dto = study_list_composer._create_study(
            study_dir, antares_version, is_xpansion_study
        )
        # then
        assert new_study_dto.xpansion_mode == "r"

    @pytest.mark.unit_test
    def test_given_xpansion_mode_option_when_create_study_is_called_then_run_mode_value_of_dto_is_xpansion_mode(
        self,
    ):
        # given
        self.parameters.xpansion_mode = "r"
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=mock.Mock(),
            parameters=self.parameters,
        )

        study_dir = study_list_composer._studies_in_dir
        antares_version = 700
        is_xpansion_study = "r"
        # when
        new_study_dto = study_list_composer._create_study(
            study_dir, antares_version, is_xpansion_study
        )
        # then
        assert new_study_dto.run_mode == Modes.xpansion_r

    @pytest.mark.unit_test
    def test_given_xpansion_mode_option_when_update_study_only_xpansion_studies_are_saved_in_database(
        self,
    ):
        # given
        self.parameters.xpansion_mode = "r"
        study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=mock.Mock(),
            display=mock.Mock(),
            parameters=self.parameters,
        )
        study_list_composer._update_database_with_study = mock.Mock()
        study_list_composer.get_antares_version = mock.Mock(return_value="610")

        study_dir = study_list_composer._studies_in_dir
        is_xpansion_study = True
        study_list_composer._is_xpansion_study = mock.Mock(
            return_value=is_xpansion_study
        )
        study_list_composer._update_database_with_directory(study_dir)

        isnot_xpansion_study = False
        study_list_composer._is_xpansion_study = mock.Mock(
            return_value=isnot_xpansion_study
        )
        # when
        study_list_composer._update_database_with_directory(study_dir)
        # then
        study_list_composer._update_database_with_study.assert_called_once()

    @pytest.mark.unit_test
    def test_given_a_study_path_when_is_there_candidates_file_is_called_return_true_if_present(
        self,
    ):
        # given
        directory_path = DATA_DIR.joinpath("xpansion-reference")
        file_manager = FileManager(display_terminal=mock.Mock())
        my_study_list_composer = StudyListComposer(
            repo=mock.Mock(),
            file_manager=file_manager,
            display=mock.Mock(),
            parameters=self.parameters,
        )

        # when
        output = my_study_list_composer._is_there_candidates_file(directory_path)
        # then
        assert output
