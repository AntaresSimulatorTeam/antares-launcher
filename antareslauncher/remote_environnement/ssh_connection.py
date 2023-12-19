import contextlib
import fnmatch
import functools
import logging
import socket
import stat
import textwrap
import time
import typing as t
from pathlib import Path, PurePosixPath

import paramiko

RemotePath = PurePosixPath
LocalPath = Path

PARAMIKO_SSH_ERROR = "Paramiko SSH Exception"
REMOTE_CONNECTION_ERROR = "Failed to connect to remote host"
IO_ERROR = "IO Error"
FILE_NOT_FOUND_ERROR = "File not found error"
DIRECTORY_NOT_FOUND_ERROR = "Directory not found error"


def retry(
    exception: t.Type[Exception],
    *exceptions: t.Type[Exception],
    delay_sec: float = 5,
    max_retry: int = 5,
    msg_fmt: str = "Retrying in {delay_sec} seconds...",
):
    """
    Decorator to retry a function call if it raises an exception.

    Args:
        exception: The exception to catch.
        exceptions: Additional exceptions to catch.
        delay_sec: The delay (in seconds) between each retry.
        max_retry: The maximum number of retries.
        msg_fmt: The message to display when retrying, with the following format keys:
            - delay_sec: The delay (in seconds) between each retry.
            - remaining: The number of remaining retries.

    Returns:
        The decorated function.
    """

    def decorator(func):  # type: ignore
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            for attempt in range(max_retry):
                try:
                    return func(*args, **kwargs)
                except (exception, *exceptions):
                    logger = logging.getLogger(__name__)
                    remaining = max_retry - attempt - 1
                    logger.warning(msg_fmt.format(delay_sec=delay_sec, remaining=remaining))
                    time.sleep(delay_sec)
            # Last attempt
            return func(*args, **kwargs)

        return wrapper

    return decorator


def retry(
    exception: t.Type[Exception],
    *exceptions: t.Type[Exception],
    delay_sec: float = 5,
    max_retry: int = 5,
    msg_fmt: str = "Retrying in {delay_sec} seconds...",
):
    """
    Decorator to retry a function call if it raises an exception.

    Args:
        exception: The exception to catch.
        exceptions: Additional exceptions to catch.
        delay_sec: The delay (in seconds) between each retry.
        max_retry: The maximum number of retries.
        msg_fmt: The message to display when retrying, with the following format keys:
            - delay_sec: The delay (in seconds) between each retry.
            - remaining: The number of remaining retries.

    Returns:
        The decorated function.
    """

    def decorator(func):  # type: ignore
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            for attempt in range(max_retry):
                try:
                    return func(*args, **kwargs)
                except (exception, *exceptions):
                    logger = logging.getLogger(__name__)
                    remaining = max_retry - attempt - 1
                    logger.warning(msg_fmt.format(delay_sec=delay_sec, remaining=remaining))
                    time.sleep(delay_sec)
            # Last attempt
            return func(*args, **kwargs)

        return wrapper

    return decorator


class SshConnectionError(Exception):
    """
    SSH Connection Error
    """


class InvalidConfigError(SshConnectionError):
    def __init__(self, config: t.Mapping[str, t.Any], msg: str = ""):
        err_msg = f"Invalid configuration error {config}"
        if msg:
            err_msg += f": {msg}"
        super().__init__(err_msg)


class ConnectionFailedException(SshConnectionError):
    def __init__(self, hostname: str, port: int, username: str):
        msg = (
            f"Unable to connect to {hostname} on port {port} with username {username}."
            f" Please ensure that the hostname, port, and username are correct, and"
            f" that the server is reachable and accepting SSH connections."
            f" If you are using a password to authenticate, please double-check that"
            f" the password is correct. If you are using a private key, please ensure"
            f" that the key is in the correct format and that you have specified"
            f" the correct path to the key file."
        )
        super().__init__(msg)


class DownloadMonitor:
    """
    A class that monitors the progress of a download.

    Args:
        total_size: The total size of the file being downloaded (in bytes).
        msg: The message to display while downloading. Defaults to "Downloading...".
        logger: A logger object for logging progress messages. Defaults to `None`.

    Attributes:
        total_size: The total size of the file being downloaded.
        msg: The message to display while downloading.
        logger: A logger object for logging progress messages.
    """

    def __init__(self, total_size: int, msg: str = "", logger=None) -> None:
        self.total_size = total_size
        self.msg = msg or "Downloading..."
        self.logger = logger or logging.getLogger(__name__)
        # The start time of the download use to calculate ETA
        self._start_time: float = time.time()
        # The amount of data (in bytes) that has been transferred so far
        # for each file
        self._transferred: int = 0
        # The total amount of data that has been transferred so far (in bytes)
        self._accumulated: int = 0
        # The progress of the download, as a percentage (0-100)
        self._progress: int = 0

    def __call__(self, transferred: int, subtotal: int) -> None:
        """
        Called when data is transferred during the download.
        Updates the progress and logs a message if progress has changed.

        Args:
            transferred: The amount of data transferred in the current transfer (in bytes).
            subtotal: The total amount of data transferred so far in this download (in bytes).
        """
        if not self.total_size:
            return
        self._transferred = transferred
        # Avoid emitting too many messages
        rate = (self._accumulated + self._transferred) / self.total_size
        if self._progress != int(rate * 10):
            self._progress = int(rate * 10)
            self.logger.info(str(self))

    def __str__(self) -> str:
        """
        Returns a string representation of the current progress.
        """
        total_transferred = self._accumulated + self._transferred
        rate = total_transferred / self.total_size
        if total_transferred:
            # Calculate ETA and progress rate
            # 0        curr_size                   total_size
            # |----------->|--------------------------->|
            # 0        duration                    total_duration
            # 0%       percent                         100%
            duration = time.time() - self._start_time
            eta = int(duration * (self.total_size - total_transferred) / total_transferred)
            return f"{self.msg:<20} ETA: {eta}s [{rate:.0%}]"
        return f"{self.msg:<20} ETA: ??? [{rate:.0%}]"

    def accumulate(self) -> None:
        """
        Accumulates the quantity transferred by the previous transfer and
        the current transfer.

        This function is used to keep track of the total quantity of data transferred
        across multiple transfers. The accumulated quantity is calculated by adding
        the quantity transferred in the current transfer to the quantity transferred
        in the previous transfer.
        """
        self._accumulated += self._transferred


class SshConnection:
    """Class to _connect to remote server"""

    def __init__(self, config: t.Mapping[str, t.Any]):
        """
        Initialize the SSH connection.

        Args:
            config: Dictionary containing the "hostname" (name or IP), "username", "port" (default is 22),
            "password" (not compulsory if private_key_file is given), "private_key_file": path to private rsa key
        """
        super(SshConnection, self).__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._client = None
        self._home_dir = ""
        self.timeout = 10
        self.host = ""
        self.username = ""
        self.port = 22
        self.password = None
        self.private_key = None

        if config:
            self.logger.info("Loading ssh connection from config dictionary")
            self._init_from_config(config)
        else:
            error = InvalidConfigError(config, "missing values: 'hostname', 'username', 'password'...")
            self.logger.debug(str(error))
            raise error
        self.initialize_home_dir()
        self.logger.info(f"Connection created with host = {self.host} and username = {self.username}")

    def _init_public_key(self, key_file_name: str, key_password: str) -> bool:
        """Initialises self.private_key

        Args:
            key_file_name: The file name of the private key

        Returns:
            True if a valid key was found, False otherwise
        """
        try:
            self.private_key = paramiko.Ed25519Key.from_private_key_file(filename=key_file_name)
            return True
        except paramiko.SSHException:
            try:
                self.private_key = paramiko.RSAKey.from_private_key_file(filename=key_file_name, password=key_password)
                return True
            except paramiko.SSHException:
                self.private_key = None
                return False

    def _init_from_config(self, config: t.Mapping[str, t.Any]) -> None:
        self.host = config.get("hostname", "")
        self.username = config.get("username", "")
        self.port = config.get("port", 22)
        self.password = config.get("password")
        key_password = config.get("key_password")
        if key_file := config.get("private_key_file"):
            self._init_public_key(key_file_name=key_file, key_password=key_password)
        elif self.password is None:
            error = InvalidConfigError(config, "missing 'password'")
            self.logger.debug(str(error))
            raise error

    def initialize_home_dir(self) -> None:
        """Initializes self._home_dir with the home directory retrieved by started "echo $HOME" connecting to the
        remote server
        """
        output, _ = self.execute_command("echo $HOME")
        self._home_dir = str(output).split()[0]

    @property
    def home_dir(self) -> str:
        """

        Returns:
            The home directory of the remote server
        """
        return self._home_dir

    @contextlib.contextmanager
    def ssh_client(self) -> t.Generator[paramiko.SSHClient, None, None]:
        client = paramiko.SSHClient()
        try:
            try:
                # Paramiko.SSHClient can be used to make connections to the remote server and transfer files
                # Parsing an instance of the AutoAddPolicy to set_missing_host_key_policy()
                # changes it to allow any host.
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # Connect to the server
                if self.private_key:
                    client.connect(
                        hostname=self.host,
                        port=self.port,
                        username=self.username,
                        pkey=self.private_key,
                        timeout=self.timeout,
                        allow_agent=False,
                    )
                    # look_for_keys=False disable searching for discoverable private key files in ~/.ssh/
                else:
                    client.connect(
                        hostname=self.host,
                        port=self.port,
                        username=self.username,
                        password=self.password,
                        timeout=self.timeout,
                        allow_agent=False,
                        look_for_keys=False,
                    )
            except paramiko.AuthenticationException as e:
                self.logger.exception(f"paramiko.AuthenticationException: {paramiko.AuthenticationException}")
                raise ConnectionFailedException(self.host, self.port, self.username) from e
            except paramiko.SSHException as e:
                self.logger.exception(f"paramiko.SSHException: {paramiko.SSHException}")
                raise ConnectionFailedException(self.host, self.port, self.username) from e
            except socket.timeout as e:
                self.logger.exception(f"socket.timeout: {socket.timeout}")
                raise ConnectionFailedException(self.host, self.port, self.username) from e
            except socket.error as e:
                self.logger.exception(f"socket.error: {socket.error}")
                raise ConnectionFailedException(self.host, self.port, self.username) from e

            yield client
        finally:
            client.close()

    def execute_command(self, command: str) -> t.Tuple[t.Optional[str], str]:
        """
        Runs an SSH command with a retry logic.

        If it encounters an SSH Exception, it's going to sleep for 5 seconds.
        The command will then be re-executed a maximum of 5 times.
        It allows us to wait for the connection to be re-established.
        This way, we avoid having a simulation failure due to an SSH error.

        Args:
            command: String containing the command that will be executed through the ssh connection

        Returns:
            output: The standard output of the command
            error: The standard error of the command
        """
        output = None

        try:
            output, error = self._exec_command(command)
        except socket.timeout:
            error = f"SSH command timed out: [{command}]"
        except paramiko.SSHException as e:
            error = f"SSH command failed to execute [{command}]: {e}"
        except ConnectionFailedException as e:
            error = f"SSH connection failed: {e}"

        if error:
            self.logger.error(error)

        return output, error

    @retry(
        socket.timeout,
        paramiko.SSHException,
        ConnectionFailedException,
        delay_sec=5,
        max_retry=5,
        msg_fmt=(
            "An SSH Error occurred, so the command did not succeed."
            " The command will be re-executed {remaining} times until it succeeds."
            " Retrying in {delay_sec} seconds..."
        ),
    )
    def _exec_command(self, command: str) -> t.Tuple[str, str]:
        """
        Executes a command on the remote host.

        Args:
            command: String containing the command that will be executed through the ssh connection

        Returns:
            output: The standard output of the command
            error: The standard error of the command
        """
        with self.ssh_client() as client:
            self.logger.info(f"Running SSH command [{command}]...")
            _, stdout, stderr = client.exec_command(command, timeout=30)
            output = stdout.read().decode("utf-8").strip()
            error = stderr.read().decode("utf-8").strip()
            self.logger.info(f"SSH command stdout:\n{textwrap.indent(output, 'SSH OUTPUT> ')}")
            self.logger.info(f"SSH command stderr:\n{textwrap.indent(error, 'SSH ERROR> ')}")
            return output, error

    def upload_file(self, src: str, dst: str):
        """Uploads a file to a remote server via sftp protocol

        Args:
            src: Local file to upload
            dst: Remote directory where the file will be uploaded

        Returns:
            True if the file has been uploaded, False otherwise
        """
        result_flag = True
        try:
            with self.ssh_client() as client:
                self.logger.info(f"Uploading file {src} to remote directory {dst}")
                sftp_client = client.open_sftp()
                sftp_client.put(src, dst)
                sftp_client.close()
        except paramiko.SSHException:
            self.logger.debug(PARAMIKO_SSH_ERROR, exc_info=True)
            result_flag = False
        except IOError:
            self.logger.debug(IO_ERROR, exc_info=True)
            result_flag = False
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            result_flag = False
        return result_flag

    def download_file(self, src: str, dst: str) -> bool:
        """Downloads a file from a remote server via sftp protocol

        Args:
            src: Remote file to download

            dst: Local directory where the file will be downloaded, dst must be full path + filename.txt

        Returns:
            True if the file has been downloaded, False otherwise
        """
        self.logger.info(f'Downloading remote file "{src}" to directory "{dst}"')
        try:
            with self.ssh_client() as client:
                sftp_client = client.open_sftp()
                sftp_client.get(src, dst)
                sftp_client.close()
                result_flag = True
        except paramiko.SSHException:
            self.logger.error(PARAMIKO_SSH_ERROR, exc_info=True)
            result_flag = False
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            result_flag = False
        return result_flag

    def download_files(
        self,
        src_dir: RemotePath,
        dst_dir: LocalPath,
        pattern: str,
        *patterns: str,
        remove: bool = True,
    ) -> t.Sequence[LocalPath]:
        """
        Download files matching the specified patterns from the remote
        source directory to the local destination directory,
        and remove them when the download is finished.

        Args:
            src_dir: Remote source directory.

            dst_dir: Local destination directory.

            pattern: Unix shell-style wildcards to match the files to download.

            patterns: Additional Unix shell-style wildcards.

            remove: if `True`, the remote file is removed after download.

        Returns:
            The paths of the downloaded files on the local filesystem.
        """
        try:
            return self._download_files(src_dir, dst_dir, (pattern,) + patterns, remove=remove)
        except TimeoutError as exc:
            self.logger.error(f"Timeout: {exc}", exc_info=True)
            return []
        except paramiko.SSHException:
            self.logger.error(PARAMIKO_SSH_ERROR, exc_info=True)
            return []
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            return []

    def _download_files(
        self,
        src_dir: RemotePath,
        dst_dir: LocalPath,
        patterns: t.Tuple[str, ...],
        *,
        remove: bool = True,
    ) -> t.Sequence[LocalPath]:
        """
        Download files matching the specified patterns from the remote
        source directory to the local destination directory.

        Args:
            src_dir: Remote source directory.

            dst_dir: Local destination directory.

            patterns: A tuple of Unix shell-style wildcards to match the files to download.

            remove: if `True`, the remote file is removed after download.

        Returns:
            The paths of the downloaded files on the local filesystem.
        """
        with self.ssh_client() as client:
            with contextlib.closing(client.open_sftp()) as sftp:  # type: paramiko.sftp_client.SFTPClient
                # Get list of files to download
                remote_attrs = sftp.listdir_attr(str(src_dir))
                remote_files = [file_attr.filename for file_attr in remote_attrs]
                total_size = sum((file_attr.st_size or 0) for file_attr in remote_attrs)
                files_to_download = [
                    f for f in remote_files if any(fnmatch.fnmatch(f, pattern) for pattern in patterns)
                ]
                # Monitor the download progression
                monitor = DownloadMonitor(total_size, logger=self.logger)
                # First get all, then delete all (for reentrancy)
                count = len(files_to_download)
                for no, filename in enumerate(files_to_download, 1):
                    monitor.msg = f"Downloading '{filename}' [{no}/{count}]..."
                    monitor.accumulate()
                    src_path = src_dir.joinpath(filename)
                    dst_path = dst_dir.joinpath(filename)
                    sftp.get(str(src_path), str(dst_path), monitor)
                if remove:
                    for filename in files_to_download:
                        src_path = src_dir.joinpath(filename)
                        sftp.remove(str(src_path))
                return [dst_dir.joinpath(filename) for filename in files_to_download]

    def check_remote_dir_exists(self, dir_path):
        """Checks if a remote path is a directory

        Args:
            dir_path: Remote path

        Returns:
            True if the directory exists, False otherwise

        Raises:
            IOError if the path exists and is a file
        """
        result_flag = False
        try:
            with self.ssh_client() as client:
                sftp_client = client.open_sftp()
                self.logger.info(f"Checking remote dir {dir_path} exists")
                sftp_stat = sftp_client.stat(dir_path)
                sftp_client.close()
                if stat.S_ISDIR(sftp_stat.st_mode):
                    result_flag = True
                else:
                    raise IOError
        except FileNotFoundError:
            self.logger.debug(FILE_NOT_FOUND_ERROR, exc_info=True)
            result_flag = False
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            result_flag = False
        return result_flag

    def check_file_not_empty(self, file_path):
        """Checks if a remote file exists and is not empty

        Args:
            file_path: Path on the remote server

        Returns:
            True if file exists and is not empty, False otherwise

        Raises:
            IOError if path exists, and it is a directory
        """
        result_flag = False
        try:
            with self.ssh_client() as client:
                sftp_client = client.open_sftp()
                self.logger.info(f'Checking remote file "{file_path}" not empty')
                sftp_stat = sftp_client.stat(file_path)
                sftp_client.close()
                if stat.S_ISREG(sftp_stat.st_mode):
                    result_flag = sftp_stat.st_size > 0
                else:
                    raise IOError(f"Not a regular file: '{file_path}'")
        except FileNotFoundError:
            self.logger.debug(FILE_NOT_FOUND_ERROR, exc_info=True)
            result_flag = False
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            result_flag = False
        return result_flag

    def make_dir(self, dir_path):
        """Creates a remote directory if it does not exist yet

        Args:
            dir_path: Remote path of the directory that will be created

        Returns:
            True if path exists or the directory is successfully created, False otherwise

        Raises:
            IOError if the path exists, and it is a file
        """
        try:
            with self.ssh_client() as client:
                sftp_client = client.open_sftp()
                try:
                    self.logger.info(f"Checking if remote directory {dir_path} exists")
                    sftp_stat = sftp_client.stat(dir_path)
                    result_flag = stat.S_ISDIR(sftp_stat.st_mode)
                except FileNotFoundError:
                    self.logger.info(f"Creating remote directory {dir_path}")
                    sftp_client.mkdir(dir_path)
                    result_flag = True
                finally:
                    sftp_client.close()
        except paramiko.SSHException:
            self.logger.debug("Paramiko SSHException", exc_info=True)
            result_flag = False
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            result_flag = False
        return result_flag

    def remove_file(self, file_path):
        """Removes a remote file

        Args:
            file_path: Path on the remote server

        Returns:
            True if file is successfully removed, False otherwise

        Raises:
            IOError if path exists, and it is a directory
        """
        try:
            with self.ssh_client() as client:
                sftp_client = client.open_sftp()
                try:
                    self.logger.info(f"Removing remote file {file_path}")
                    sftp_stat = sftp_client.stat(file_path)
                    if not stat.S_ISREG(sftp_stat.st_mode):
                        raise IOError(f"Not a regular file: '{file_path}'")
                    with contextlib.suppress(IOError):
                        sftp_client.remove(file_path)
                    result_flag = True
                except FileNotFoundError:
                    self.logger.debug("FileNotFound nothing to remove", exc_info=True)
                    result_flag = True
                finally:
                    sftp_client.close()
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            result_flag = False
        return result_flag

    def remove_dir(self, dir_path):
        """Removes a remote directory

        Args:
            dir_path: Path on the remote server

        Returns:
            True if the directory is successfully removed, False otherwise

        Raises:
            IOError if path exists, and it is a file
        """
        try:
            with self.ssh_client() as client:
                sftp_client = client.open_sftp()
                try:
                    self.logger.info(f"Removing remote directory {dir_path}")
                    sftp_stat = sftp_client.stat(dir_path)
                    if not stat.S_ISDIR(sftp_stat.st_mode):
                        raise IOError(f"Not a directory: '{dir_path}'")
                    with contextlib.suppress(IOError):
                        sftp_client.rmdir(dir_path)
                    result_flag = True
                except FileNotFoundError:
                    self.logger.debug(DIRECTORY_NOT_FOUND_ERROR, exc_info=True)
                    result_flag = True
                finally:
                    sftp_client.close()
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            result_flag = False
        return result_flag

    def test_connection(self) -> bool:
        try:
            with self.ssh_client():
                return True
        except ConnectionFailedException:
            self.logger.error(REMOTE_CONNECTION_ERROR, exc_info=True)
            return False
