import typing as t
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.download_final_zip import FinalZipDownloader


def download_final_zip(study: StudyDTO) -> t.Optional[Path]:
    """Simulate the download of the final ZIP."""
    dst_dir = Path(study.output_dir)  # must exist
    out_path = dst_dir.joinpath(f"finished_{study.name}_{study.job_id}.zip")
    out_path.write_bytes(b"PK fake zip")
    return out_path


class TestFinalZipDownloader:
    @pytest.mark.unit_test
    def test_download__pending_study(self, pending_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = FinalZipDownloader(env=env, display=display)
        downloader.download(pending_study)

        # Check the result
        env.download_final_zip.assert_not_called()
        display.show_message.assert_not_called()
        display.show_error.assert_not_called()

    @pytest.mark.unit_test
    def test_download__started_study(self, started_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = FinalZipDownloader(env=env, display=display)
        downloader.download(started_study)

        # Check the result
        env.download_final_zip.assert_not_called()
        display.show_message.assert_not_called()
        display.show_error.assert_not_called()

    @pytest.mark.unit_test
    def test_download__with_error_study(self, with_error_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = FinalZipDownloader(env=env, display=display)
        downloader.download(with_error_study)

        # Check the result
        env.download_final_zip.assert_called()
        display.show_message.assert_called()
        display.show_error.assert_not_called()

    @pytest.mark.unit_test
    def test_download__finished_study__download_ok(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.download_final_zip = download_final_zip
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = FinalZipDownloader(env=env, display=display)
        downloader.download(finished_study)

        # Check the result: one ZIP file is downloaded
        assert finished_study.local_final_zipfile_path
        assert display.show_message.call_count == 2  # two messages
        assert display.show_error.call_count == 0  # no error
        output_dir = Path(finished_study.output_dir)
        assert output_dir.is_dir()
        zip_files = list(output_dir.iterdir())
        assert len(zip_files) == 1

    @pytest.mark.unit_test
    def test_download__finished_study__reentrancy(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.download_final_zip = download_final_zip
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download twice
        downloader = FinalZipDownloader(env=env, display=display)
        downloader.download(finished_study)

        output_dir1 = Path(finished_study.output_dir)
        zip_files1 = set(output_dir1.iterdir())
        downloader.download(finished_study)

        # Check the result: one ZIP file is downloaded
        assert finished_study.local_final_zipfile_path
        assert display.show_message.call_count == 2
        assert display.show_error.call_count == 0

        # ZIP files are not duplicated
        output_dir2 = Path(finished_study.output_dir)
        zip_files2 = set(output_dir2.iterdir())
        assert zip_files1 == zip_files2

    @pytest.mark.unit_test
    def test_download__finished_study__download_nothing(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.download_final_zip = lambda _: []
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = FinalZipDownloader(env=env, display=display)
        downloader.download(finished_study)

        # Check the result: no ZIP file is downloaded
        assert not finished_study.local_final_zipfile_path
        assert display.show_message.call_count == 1  # only the first message
        assert display.show_error.call_count == 1
        output_dir = Path(finished_study.output_dir)
        assert output_dir.is_dir()
        zip_files = list(output_dir.iterdir())
        assert not zip_files

    @pytest.mark.unit_test
    def test_download__finished_study__download_error(self, finished_study: StudyDTO) -> None:
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.download_final_zip.side_effect = Exception("Connection error")
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the download
        downloader = FinalZipDownloader(env=env, display=display)
        with pytest.raises(Exception, match=r"Connection\s+error"):
            downloader.download(finished_study)

        # Check the result: the exception is not managed
        assert not finished_study.local_final_zipfile_path
        assert display.show_message.call_count == 1  # only the first message
        display.show_error.assert_not_called()
        output_dir = Path(finished_study.output_dir)
        assert output_dir.is_dir()
        zip_files = list(output_dir.iterdir())
        assert not zip_files
