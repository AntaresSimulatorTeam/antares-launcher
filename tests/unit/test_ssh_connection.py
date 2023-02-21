import io
import logging
import time
from pathlib import Path, PurePosixPath
from typing import List
from unittest.mock import ANY, Mock, call, patch

import paramiko
import pytest
from paramiko.sftp_attr import SFTPAttributes

from antareslauncher.remote_environnement.ssh_connection import (
    DownloadMonitor,
    SshConnection,
    ConnectionFailedException,
)

LOGGER = DownloadMonitor.__module__


@pytest.mark.unit_test
class TestDownloadMinotor:
    def test_download_monitor__null_size(self, caplog):
        monitor = DownloadMonitor(0)
        with caplog.at_level(level=logging.INFO, logger=LOGGER):
            monitor(0, 0)
        assert not caplog.text

    def test_download_monitor__nominal(self, caplog):
        total_size = 1000
        monitor = DownloadMonitor(total_size, msg="Downloading 'foo'")
        with caplog.at_level(level=logging.INFO, logger=LOGGER):
            for _ in range(0, total_size, 250):
                monitor(250, 0)
                time.sleep(0.01)
        assert caplog.messages == [
            "Downloading 'foo'    ETA: 0s [25%]",
            "Downloading 'foo'    ETA: 0s [50%]",
            "Downloading 'foo'    ETA: 0s [75%]",
            "Downloading 'foo'    ETA: 0s [100%]",
        ]


@pytest.mark.unit_test
class TestSshConnection:
    @pytest.fixture(name="ssh_mock")
    def fixture_ssh_mock(self):
        """Mocked SSH Client"""
        ssh_mock = Mock(spec=paramiko.SSHClient)
        ssh_mock.connect.return_value = Mock()
        # result for `SshConnection.initialize_home_dir`
        ssh_mock.exec_command.return_value = (
            io.BytesIO(b""),
            io.BytesIO(b"/home/user"),
            io.BytesIO(b""),
        )
        return ssh_mock

    @pytest.fixture(name="remote_attrs")
    def fixture_remote_attrs(self, tmp_path) -> List[SFTPAttributes]:
        # Yes I know, this is a little stupid to create temporary files,
        # but it's an efficient way to get the file stats...
        remote_files = [
            ("foo.txt", 1024 * 2),
            ("bar.zip", 1024 * 50),
            ("foobar.log", 1024 * 5),
        ]
        remote_attrs = []
        for filename, size in remote_files:
            remote_path = tmp_path.joinpath(filename)
            remote_path.write_bytes(b"a" * size)
            remote_attrs.append(SFTPAttributes.from_stat(remote_path.stat(), filename))
        return remote_attrs

    def test_download_files(self, remote_attrs, ssh_mock, caplog):
        sftp = Mock(spec=paramiko.sftp_client.SFTPClient)
        sftp.listdir_attr.return_value = remote_attrs
        ssh_mock.open_sftp.return_value = sftp

        with patch("paramiko.SSHClient", return_value=ssh_mock):
            config = {
                "hostname": "slurm-server",
                "username": "john.doe",
                "password": "s3cr3T",
            }
            connection = SshConnection(config)
            src_dir = PurePosixPath("/workspace")
            dst_dir = Path("/path/to/study")
            with caplog.at_level(level=logging.ERROR, logger=LOGGER):
                actual = connection.download_files(src_dir, dst_dir, "*.txt", "*.zip")

        # ensure that no error is reported
        assert not caplog.text, caplog.text
        assert actual == [
            Path("/path/to/study/foo.txt"),
            Path("/path/to/study/bar.zip"),
        ]
        assert sftp.get.mock_calls == [
            # We use str(Path("...")) because Path could be a WindowsPath which use "/" instead of "\"
            call("/workspace/foo.txt", str(Path("/path/to/study/foo.txt")), ANY),
            call("/workspace/bar.zip", str(Path("/path/to/study/bar.zip")), ANY),
        ]
        assert sftp.remove.mock_calls == [
            call("/workspace/foo.txt"),
            call("/workspace/bar.zip"),
        ]

    @pytest.mark.parametrize(
        "exception",
        [
            TimeoutError("an error occurs"),
            paramiko.SSHException("an error occurs"),
            ConnectionFailedException("hostname", 21, "an error occurs"),
        ],
    )
    def test_download_files__timeout(self, remote_attrs, ssh_mock, exception, caplog):
        sftp = Mock(spec=paramiko.sftp_client.SFTPClient)
        sftp.listdir_attr.return_value = remote_attrs
        sftp.get.side_effect = exception
        ssh_mock.open_sftp.return_value = sftp

        with patch("paramiko.SSHClient", return_value=ssh_mock):
            config = {
                "hostname": "slurm-server",
                "username": "john.doe",
                "password": "s3cr3T",
            }
            connection = SshConnection(config)
            src_dir = PurePosixPath("/workspace")
            dst_dir = Path("/path/to/study")
            with caplog.at_level(level=logging.ERROR, logger=LOGGER):
                actual = connection.download_files(src_dir, dst_dir, "*.txt", "*.zip")

        # ensure that no error is reported
        assert "an error occurs" in caplog.text, caplog.text
        assert not actual
        assert sftp.get.mock_calls == [
            # We use str(Path("...")) because Path could be a WindowsPath which use "/" instead of "\"
            call("/workspace/foo.txt", str(Path("/path/to/study/foo.txt")), ANY),
        ]
        assert sftp.remove.mock_calls == []
