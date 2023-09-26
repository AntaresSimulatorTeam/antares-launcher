import zipfile
from pathlib import Path, PurePosixPath
from unittest import mock

import pytest

from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch.launch_controller import LaunchController, StudyLauncher
from antareslauncher.use_cases.launch.study_submitter import StudySubmitter
from antareslauncher.use_cases.launch.study_zip_uploader import StudyZipfileUploader

# noinspection SpellCheckingInspection
STUDY_FILES = [
    "check-config.json",
    "Desktop.ini",
    "input/areas/dummy.txt",
    "input/wind/dummy.txt",
    "layers/layers.ini",
    "output/20230321-1901eco/dummy.txt",
    "output/20230321-1901eco.zip",
    "output/20230926-1230adq/dummy.txt",
    "settings/comments.txt",
    "settings/generaldata.ini",
    "settings/resources/dummy.txt",
    "settings/scenariobuilder.dat",
    "study.antares",
]


def prepare_study_data(study_dir: Path) -> None:
    for file in STUDY_FILES:
        file_path = study_dir.joinpath(file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()


@pytest.fixture(name="ready_study")
def ready_study_fixture(pending_study: StudyDTO) -> StudyDTO:
    """Prepare the study data and return the study."""
    study_dir = Path(pending_study.path)
    prepare_study_data(study_dir)
    return pending_study


@pytest.fixture(name="study_uploaded")
def study_uploaded_fixture(tmp_path: Path) -> StudyDTO:
    study_path = tmp_path.joinpath("upload-failure")
    job_log_dir = tmp_path.joinpath("LOG_DIR")
    output_dir = tmp_path.joinpath("OUTPUT_DIR")
    study = StudyDTO(
        path=str(study_path),
        started=False,
        job_log_dir=str(job_log_dir),
        output_dir=str(output_dir),
        zipfile_path="",
        zip_is_sent=False,
        job_id=0,
    )
    study_dir = Path(study.path)
    prepare_study_data(study_dir)
    return study


@pytest.fixture(name="study_submitted")
def study_submitted_fixture(tmp_path: Path) -> StudyDTO:
    study_path = tmp_path.joinpath("submit-failure")
    job_log_dir = tmp_path.joinpath("LOG_DIR")
    output_dir = tmp_path.joinpath("OUTPUT_DIR")
    study = StudyDTO(
        path=str(study_path),
        started=False,
        job_log_dir=str(job_log_dir),
        output_dir=str(output_dir),
        zipfile_path="",
        zip_is_sent=False,
        job_id=0,
    )
    study_dir = Path(study.path)
    prepare_study_data(study_dir)
    return study


class TestStudyLauncher:
    """
    The gaol is to test the launching of a study.
    Every call to the remote environment is mocked.
    """

    @pytest.mark.unit_test
    def test_launch_study__nominal_case(self, ready_study: StudyDTO) -> None:
        """
        Test the nominal case of launching a study.

        - The study directory must be correctly compressed.
        - The `upload` method of the `study_uploader` must be called.
        - The ZIP file must be removed after the upload.
        - The `submit_job` method of the `study_submitter` must be called.
        - The `save_study` method of the `data_repo` must be called.
        """

        class Uploader:
            def __init__(self):
                self.actual_names = frozenset()

            def upload(self, study: StudyDTO) -> None:
                """Simulate the upload and check that the ZIP file has been correctly created."""
                zip_path = Path(study.zipfile_path)
                with zipfile.ZipFile(zip_path, mode="r") as zf:
                    # keep only file names, excluding directories
                    self.actual_names = frozenset(name for name in zf.namelist() if "." in name)
                study.zip_is_sent = True

            __call__ = upload

        upload = Uploader()

        def submit_job(study: StudyDTO) -> None:
            """Simulate the submission of the job."""
            study.job_id = 40414243

        # Given
        study_uploader = mock.Mock(spec=StudyZipfileUploader)
        study_uploader.upload = upload
        study_uploader.remove = mock.Mock()

        study_submitter = mock.Mock(spec=StudySubmitter)
        study_submitter.submit_job = submit_job

        data_repo = mock.Mock(spec=DataRepoTinydb)
        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = mock.Mock(side_effect=lambda x, **kwargs: x)
        study_launcher = StudyLauncher(study_uploader, study_submitter, data_repo, display)

        # When
        study_launcher.launch_study(ready_study)

        # Then
        prefix_path = PurePosixPath(ready_study.name)
        expected_names = frozenset([prefix_path.joinpath(name).as_posix() for name in STUDY_FILES])
        assert upload.actual_names == expected_names

        assert ready_study.zipfile_path, "The ZIP file should have been created"
        assert ready_study.zip_is_sent, "The ZIP file should have been uploaded"
        assert ready_study.job_id == 40414243, "The job should have been submitted"
        assert not ready_study.with_error, "The study should not be marked as failed"

        assert not Path(ready_study.zipfile_path).exists(), "The ZIP file should have been removed"

        study_uploader.remove.assert_not_called()
        data_repo.save_study.assert_called_once()

    @pytest.mark.parametrize("scenario", ["set_false", "raise_exception"])
    @pytest.mark.unit_test
    def test_launch_study__upload_fails(self, ready_study: StudyDTO, scenario: str) -> None:
        def upload(study: StudyDTO) -> None:
            """Simulate the upload that fails"""
            if scenario == "set_false":
                study.zip_is_sent = False
            elif scenario == "raise_exception":
                raise Exception("Upload failed")
            else:
                raise NotImplementedError(scenario)

        # Given
        study_uploader = mock.Mock(spec=StudyZipfileUploader)
        study_uploader.upload = upload

        study_submitter = mock.Mock(spec=StudySubmitter)

        data_repo = mock.Mock(spec=DataRepoTinydb)
        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = mock.Mock(side_effect=lambda x, **kwargs: x)
        study_launcher = StudyLauncher(study_uploader, study_submitter, data_repo, display)

        # When
        study_launcher.launch_study(ready_study)

        # Then
        assert ready_study.zipfile_path, "The ZIP file should have been created"
        assert not ready_study.zip_is_sent, "The ZIP file should not have been uploaded"
        assert not ready_study.job_id, "The job should not have been submitted"
        assert ready_study.with_error, "The study should be marked as failed"

        assert not Path(ready_study.zipfile_path).exists(), "The ZIP file should have been removed"

        study_submitter.submit_job.assert_not_called()
        study_uploader.remove.assert_called_once()
        data_repo.save_study.assert_called_once()

    @pytest.mark.parametrize("scenario", ["set_null", "raise_exception"])
    @pytest.mark.unit_test
    def test_launch_study__submit_job_fails(self, ready_study: StudyDTO, scenario: str) -> None:
        def upload(study: StudyDTO) -> None:
            study.zip_is_sent = True

        def submit_job(study: StudyDTO) -> None:
            """Simulate the submission of the job that fails"""
            if scenario == "set_null":
                study.job_id = 0
            elif scenario == "raise_exception":
                raise Exception("Simulation of submission failure")
            else:
                raise NotImplementedError(scenario)

        # Given
        study_uploader = mock.Mock(spec=StudyZipfileUploader)
        study_uploader.upload = upload
        study_submitter = mock.Mock(spec=StudySubmitter)
        study_submitter.submit_job = submit_job

        data_repo = mock.Mock(spec=DataRepoTinydb)
        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = mock.Mock(side_effect=lambda x, **kwargs: x)
        study_launcher = StudyLauncher(study_uploader, study_submitter, data_repo, display)

        # When
        study_launcher.launch_study(ready_study)

        # Then
        assert ready_study.zipfile_path, "The ZIP file should have been created"
        assert ready_study.zip_is_sent, "The ZIP file should have been uploaded"
        assert not ready_study.job_id, "The job should not have been submitted"
        assert ready_study.with_error, "The study should be marked as failed"

        assert not Path(ready_study.zipfile_path).exists(), "The ZIP file should have been removed"

        study_uploader.remove.assert_called_once()
        data_repo.save_study.assert_called_once()


class TestLaunchController:
    def test_launch_all_studies__nominal_case(self, ready_study: StudyDTO) -> None:
        # Given
        data_repo = mock.Mock(spec=DataRepoTinydb)
        data_repo.get_list_of_studies = mock.Mock(return_value=[ready_study])

        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.upload_file = mock.Mock(return_value=True)
        env.submit_job = mock.Mock(return_value=40414243)

        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = mock.Mock(side_effect=lambda x, **kwargs: x)

        launch_controller = LaunchController(data_repo, env, display)

        # When
        launch_controller.launch_all_studies()

        # Then
        assert ready_study.zipfile_path, "The ZIP file should have been created"
        assert ready_study.zip_is_sent, "The ZIP file should have been uploaded"
        assert ready_study.job_id == 40414243, "The job should have been submitted"
        assert not ready_study.with_error, "The study should not be marked as failed"

        assert not Path(ready_study.zipfile_path).exists(), "The ZIP file should have been removed"

        data_repo.save_study.assert_called_once()

    def test_launch_all_studies__bad_studies(
        self,
        study_uploaded: StudyDTO,
        study_submitted: StudyDTO,
        ready_study: StudyDTO,
    ) -> None:
        """
        We want to check that even if some studies fail on download or submission,
        all valid studies are processed correctly.
        """

        def upload_file(src: str) -> bool:
            return "upload-failure" not in src

        class JobSubmitter:
            def __init__(self):
                self.job_id = 0

            def __call__(self, study: StudyDTO) -> int:
                self.job_id += 1
                return 0 if study.name == "submit-failure" else self.job_id

        # Given
        data_repo = mock.Mock(spec=DataRepoTinydb)
        studies = [study_uploaded, study_submitted, ready_study]
        data_repo.get_list_of_studies = mock.Mock(return_value=studies)

        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.upload_file = upload_file
        env.submit_job = JobSubmitter()
        env.remove_input_zipfile = mock.Mock(return_value=True)

        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = mock.Mock(side_effect=lambda x, **kwargs: x)

        launch_controller = LaunchController(data_repo, env, display)

        # When
        launch_controller.launch_all_studies()

        # Then
        actual_states = [
            {"zip_is_sent": study.zip_is_sent, "job_id": study.job_id, "with_error": study.with_error}
            for study in studies
        ]

        # In case of upload failure, the remote ZIP file is
        expected_states = [
            {"zip_is_sent": False, "job_id": 0, "with_error": True},
            {"zip_is_sent": False, "job_id": 0, "with_error": True},
            {"zip_is_sent": True, "job_id": 2, "with_error": False},
        ]
        assert actual_states == expected_states
