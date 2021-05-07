import copy
import getpass
from unittest import mock
from unittest.mock import call

import pytest

import antareslauncher.use_cases.launch.study_submitter
import antareslauncher.use_cases.launch.study_zip_uploader
from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch import launch_controller
from antareslauncher.use_cases.launch.launch_controller import StudyLauncher
from antareslauncher.use_cases.launch.study_submitter import StudySubmitter
from antareslauncher.use_cases.launch.study_zip_cleaner import StudyZipCleaner
from antareslauncher.use_cases.launch.study_zip_uploader import (
    StudyZipfileUploader,
)
from antareslauncher.use_cases.launch.study_zipper import StudyZipper


class TestStudyLauncher:
    def setup_method(self):
        env = mock.Mock(spec_set=IRemoteEnvironment)
        display = mock.Mock(spec_set=IDisplay)
        file_manager = mock.Mock(spec_set=FileManager)
        repo = mock.Mock(spec_set=IDataRepo)
        self.reporter = DataReporter(repo)
        self.zipper = StudyZipper(file_manager, display)
        self.study_uploader = StudyZipfileUploader(env, display)
        self.zipfile_cleaner = StudyZipCleaner(file_manager, display)
        self.study_submitter = StudySubmitter(env, display)
        self.study_launcher = StudyLauncher(
            self.zipper,
            self.study_uploader,
            self.zipfile_cleaner,
            self.study_submitter,
            self.reporter,
        )

    def test_launch_study_calls_all_four_steps(self):
        study = StudyDTO(path="hello")
        study1 = StudyDTO(path="hello1")
        self.zipper.zip = mock.Mock(return_value=study1)
        study2 = StudyDTO(path="hello2", zip_is_sent=True)
        self.study_uploader.upload = mock.Mock(return_value=study2)
        study3 = StudyDTO(path="hello3")
        self.zipfile_cleaner.remove_input_zipfile = mock.Mock(return_value=study3)
        study4 = StudyDTO(path="hello4")
        self.study_submitter.submit_job = mock.Mock(return_value=study4)
        self.reporter.save_study = mock.Mock()

        self.study_launcher.launch_study(study)

        self.zipper.zip.assert_called_once_with(study)
        self.study_uploader.upload.assert_called_once_with(study1)
        self.zipfile_cleaner.remove_input_zipfile.assert_called_once_with(study2)
        self.study_submitter.submit_job.assert_called_once_with(study3)

        assert self.reporter.save_study.call_count == 4
        calls = self.reporter.save_study.call_args_list
        assert calls[0] == call(study1)
        assert calls[1] == call(study2)
        assert calls[2] == call(study3)
        assert calls[3] == call(study4)


class TestLauncherController:
    def setup_method(self):
        self.data_repo = DataRepoTinydb("", "name")
        self.data_repo.save_study = mock.Mock()
        self.display = mock.Mock()

    @pytest.fixture(scope="function")
    def my_launch_controller(self):
        expected_study = StudyDTO(path="hello")
        list_of_studies = [copy.deepcopy(expected_study)]
        self.data_repo.get_list_of_studies = mock.Mock(return_value=list_of_studies)
        remote_env_mock = mock.Mock(spec=iremote_environment.IRemoteEnvironment)
        file_manager_mock = mock.Mock()
        my_launcher = launch_controller.LaunchController(
            self.data_repo, remote_env_mock, file_manager_mock, self.display
        )
        return my_launcher, expected_study

    def test_with_one_study_the_compressor_is_called_once(self):
        my_study = StudyDTO(path="hello")
        list_of_studies = [my_study]
        self.data_repo.get_list_of_studies = mock.Mock(return_value=list_of_studies)

        remote_env_mock = mock.Mock(spec=iremote_environment.IRemoteEnvironment)
        file_manager = mock.Mock(spec_set=FileManager)
        file_manager.zip_dir_excluding_subdir = mock.Mock()

        my_launcher = launch_controller.LaunchController(
            self.data_repo, remote_env_mock, file_manager, self.display
        )
        my_launcher.launch_all_studies()

        zipfile_path = my_study.path + "-" + getpass.getuser() + ".zip"
        file_manager.zip_dir_excluding_subdir.assert_called_once_with(
            my_study.path, zipfile_path, "output"
        )

    @pytest.mark.unit_test
    def test_given_one_study_then_repo_is_called_to_save_the_study_with_updated_zip_is_sent(
        self, my_launch_controller
    ):
        # given
        my_launcher, expected_study = my_launch_controller
        # when
        my_launcher.env.upload_file = mock.Mock(return_value=True)
        my_launcher.repo.save_study = mock.Mock()
        my_launcher.launch_all_studies()
        # then
        expected_study.zipfile_path = (
            expected_study.path + "-" + getpass.getuser() + ".zip"
        )
        second_call = my_launcher.repo.save_study.call_args_list[1]
        first_argument = second_call[0][0]
        assert first_argument.zip_is_sent

    @pytest.mark.unit_test
    def test_given_one_study_when_launcher_is_called_then_study_is_saved_with_job_id_and_submitted_flag(
        self, my_launch_controller
    ):
        # given
        my_launcher, expected_study = my_launch_controller
        # when
        my_launcher.env.upload_file = mock.Mock(return_value=True)
        my_launcher.env.submit_job = mock.Mock(return_value=42)
        my_launcher.repo.save_study = mock.Mock()
        my_launcher.launch_all_studies()
        # then
        expected_study.zipfile_path = "ciao.zip"
        expected_study.zip_is_sent = True
        fourth_call = my_launcher.repo.save_study.call_args_list[3]
        first_argument = fourth_call[0][0]
        assert first_argument.job_id == 42

    @pytest.mark.unit_test
    def test_given_one_study_when_submit_fails_then_exception_is_raised(
        self, my_launch_controller
    ):
        # given
        my_launcher, expected_study = my_launch_controller
        # when
        my_launcher.env.upload_file = mock.Mock(return_value=True)
        my_launcher.env.submit_job = mock.Mock(return_value=None)
        my_launcher.repo.save_study = mock.Mock()
        # then
        with pytest.raises(
            antareslauncher.use_cases.launch.study_submitter.FailedSubmissionException
        ):
            my_launcher.launch_all_studies()

    @pytest.mark.unit_test
    def test_given_one_study_when_zip_fails_then_return_none(
        self, my_launch_controller
    ):
        # given
        my_launcher, expected_study = my_launch_controller
        my_launcher.file_manager.zip_dir_excluding_subdir = mock.Mock(
            return_value=False
        )
        # when
        my_launcher.launch_all_studies()
        # then
        assert expected_study.zipfile_path is ""

    @pytest.mark.unit_test
    def test_given_a_sent_study_when_launch_all_studies_called_then_file_manager_remove_zip_file_is_called_once(
        self, my_launch_controller
    ):
        # given
        my_launcher, expected_study = my_launch_controller
        my_launcher._upload_zipfile = mock.Mock(return_value=True)
        my_launcher.file_manager.remove_file = mock.Mock()

        # when
        my_launcher.launch_all_studies()
        # then
        my_launcher.file_manager.remove_file.assert_called_once()
