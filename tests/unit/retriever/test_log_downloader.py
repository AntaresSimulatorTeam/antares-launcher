import typing as t
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.log_downloader import LogDownloader


def download_logs(study: StudyDTO) -> t.List[Path]:
    """Simulate the download of logs."""
    dst_dir = Path(study.job_log_dir)  # must exist
    out_path = dst_dir.joinpath(f"antares-out-{study.job_id}.txt")
    out_path.write_text("Quitting the solver gracefully.")
    err_path = dst_dir.joinpath(f"antares-err-{study.job_id}.txt")
    err_path.write_text("No error")
    return [out_path, err_path]


class TestLogDownloader:
    @pytest.mark.unit_test
    def test_run__pending_study(self, pending_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = LogDownloader(env=env, display=display)
        downloader.run(pending_study)

        # Check the result
        env.download_logs.assert_not_called()
        display.show_message.assert_not_called()
        display.show_error.assert_not_called()

    @pytest.mark.unit_test
    def test_run__started_study__download_ok(self, started_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.download_logs = download_logs
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = LogDownloader(env=env, display=display)
        downloader.run(started_study)

        # Check the result: two log files are downloaded
        assert started_study.logs_downloaded
        display.show_message.assert_called_once()
        display.show_error.assert_not_called()
        job_log_dir = Path(started_study.job_log_dir)
        assert job_log_dir.is_dir()
        log_files = list(job_log_dir.iterdir())
        assert len(log_files) == 2

    @pytest.mark.unit_test
    def test_run__started_study__reentrancy(self, started_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.download_logs = download_logs
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download twice
        downloader = LogDownloader(env=env, display=display)
        downloader.run(started_study)

        job_log_dir1 = Path(started_study.job_log_dir)
        log_files1 = set(job_log_dir1.iterdir())
        downloader.run(started_study)

        # Check the result: two log files are downloaded
        assert started_study.logs_downloaded
        assert display.show_message.call_count == 2
        assert display.show_error.call_count == 0

        # Log files are not duplicated
        job_log_dir2 = Path(started_study.job_log_dir)
        log_files2 = set(job_log_dir2.iterdir())
        assert log_files1 == log_files2

    @pytest.mark.unit_test
    def test_run__started_study__download_nothing(self, started_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.download_logs = lambda _: []
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = LogDownloader(env=env, display=display)
        downloader.run(started_study)

        # Check the result: no log file is downloaded
        assert not started_study.logs_downloaded
        display.show_message.assert_not_called()
        display.show_error.assert_called_once()
        job_log_dir = Path(started_study.job_log_dir)
        assert job_log_dir.is_dir()
        log_files = list(job_log_dir.iterdir())
        assert not log_files

    @pytest.mark.unit_test
    def test_run__started_study__download_error(self, started_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.download_logs.side_effect = Exception("Connection error")
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = LogDownloader(env=env, display=display)
        with pytest.raises(Exception, match=r"Connection\s+error"):
            downloader.run(started_study)

        # Check the result: the exception is not managed
        assert not started_study.logs_downloaded
        display.show_message.assert_not_called()
        display.show_error.assert_not_called()
        job_log_dir = Path(started_study.job_log_dir)
        assert job_log_dir.is_dir()
        log_files = list(job_log_dir.iterdir())
        assert not log_files
