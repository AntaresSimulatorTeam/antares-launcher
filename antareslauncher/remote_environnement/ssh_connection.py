import contextlib
import logging
import socket
import stat
from os.path import expanduser

import paramiko


class SshConnectionError(Exception):
    """
    SSH Connection Error
    """


class InvalidConfigError(SshConnectionError):
    def __init__(self, config, msg=""):
        err_msg = f"Invalid configuration error {config}"
        if msg:
            err_msg += f": {msg}"
        super().__init__(err_msg)


class SshConnection:
    """Class to _connect to remote server"""

    class ConnectionFailedException(Exception):
        pass

    def __init__(self, config: dict = None):
        """

        Args:
            config: Dictionary containing the "hostname" (name or IP), "username", "port" (default is 22),
            "password" (not compulsory if private_key_file is given), "private_key_file": path to private rsa key
        """
        super(SshConnection, self).__init__()
        self.logger = logging.getLogger(f"{__name__}.{__class__.__name__}")
        self.__client = None
        self.__home_dir = None
        self.timeout = 10
        self.host = ""
        self.username = ""
        self.port = 22
        self.password = None
        self.private_key = None

        if config:
            self.logger.info("Loading ssh connection from config dictionary")
            self.__init_from_config(config)
        else:
            error = InvalidConfigError(config, "missing values: 'hostname', 'username', 'password'...")
            self.logger.debug(str(error))
            raise error
        self.initialize_home_dir()
        self.logger.info(
            f"Connection created with host = {self.host} and username = {self.username}"
        )

    def __initialise_public_key(self, key_file_name, key_password):
        """Initialises self.private_key

        Args:
            key_file_name: The file name of the private key

        Returns:
            True if a valid key was found, False otherwise
        """
        try:
            self.private_key = paramiko.Ed25519Key.from_private_key_file(
                filename=key_file_name
            )
            return True
        except paramiko.SSHException:
            try:
                self.private_key = paramiko.RSAKey.from_private_key_file(
                    filename=key_file_name, password=key_password
                )
                return True
            except paramiko.SSHException:
                self.private_key = None
                return False

    def __init_from_config(self, config: dict):
        self.host = config.get("hostname", "")
        self.username = config.get("username", "")
        self.port = config.get("port", 22)
        self.password = config.get("password")
        key_password = config.get("key_password")
        if key_file := config.get("private_key_file"):
            key_file_path = expanduser(key_file)
            self.__initialise_public_key(
                key_file_name=key_file_path, key_password=key_password
            )
        elif self.password is None:
            error = InvalidConfigError(config, "missing 'password'")
            self.logger.debug(str(error))
            raise error

    def initialize_home_dir(self):
        """Initializes self.__home_dir with the home directory retrieved by started "echo $HOME" connecting to the
        remote server
        """
        output, _ = self.execute_command("echo $HOME")
        self.__home_dir = str(output).split()[0]

    @property
    def home_dir(self):
        """

        Returns:
            The home directory of the remote server
        """
        return self.__home_dir

    @contextlib.contextmanager
    def ssh_client(self):
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
            except paramiko.AuthenticationException:
                self.logger.exception(
                    f"paramiko.AuthenticationException: {paramiko.AuthenticationException}"
                )
            except paramiko.SSHException as e:
                self.logger.exception(f"paramiko.SSHException: {paramiko.SSHException}")
                raise SshConnection.ConnectionFailedException() from e
            except socket.timeout as e:
                self.logger.exception(f"socket.timeout: {socket.timeout}")
                raise SshConnection.ConnectionFailedException() from e
            except socket.error as e:
                self.logger.exception(f"socket.error: {socket.error}")
                raise SshConnection.ConnectionFailedException() from e

            yield client
        finally:
            client.close()

    def execute_command(self, command: str):
        """Executes a command on the remote host. Puts stderr and stdout in
        self.ssh_error and self.ssh_output respectively

        Args:
            command: String containing the command that will be executed through the ssh connection

        Returns:
            output: The standard output of the command

            error: The standard error of the command
        """
        output = None
        self.logger.info(f"Executing command on remote server: {command}")
        try:
            with self.ssh_client() as client:
                stdin, stdout, stderr = client.exec_command(command, timeout=30)
                output = stdout.read().decode("utf-8")
                error = stderr.read().decode("utf-8")
        except socket.timeout:
            error = f"Command timed out: {command}"
        except paramiko.SSHException:
            error = f"Failed to execute {command}"
        except SshConnection.ConnectionFailedException:
            error = f"Failed to connect to remote host and execute {command}"

        self.logger.info(f"Command output:\nOutput: {output}\nError: {error}")
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
            self.logger.debug("Paramiko SSH Exception", exc_info=True)
            result_flag = False
        except IOError:
            self.logger.debug("IO Error", exc_info=True)
            result_flag = False
        except SshConnection.ConnectionFailedException:
            self.logger.error("Failed to connect to remote host", exc_info=True)
            result_flag = False
        return result_flag

    def download_file(self, src: str, dst: str):
        """Downloads a file from a remote server via sftp protocol

        Args:
            src: Remote file to download

            dst: Local directory where the file will be downloaded, dst must be full path + filename.txt

        Returns:
            True if the file has been downloaded, False otherwise
        """
        try:
            with self.ssh_client() as client:
                self.logger.info(
                    f'Downloading remote file "{src}" to directory "{dst}"'
                )
                sftp_client = client.open_sftp()
                sftp_client.get(src, dst)
                sftp_client.close()
                result_flag = True
        except paramiko.SSHException:
            self.logger.error("Paramiko SSH Exception", exc_info=True)
            result_flag = False
        except SshConnection.ConnectionFailedException:
            self.logger.error("Failed to connect to remote host", exc_info=True)
            result_flag = False
        return result_flag

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
            self.logger.debug("FileNotFoundError", exc_info=True)
            result_flag = False
        except SshConnection.ConnectionFailedException:
            self.logger.error("Failed to connect to remote host", exc_info=True)
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
            self.logger.debug("FileNotFoundError", exc_info=True)
            result_flag = False
        except SshConnection.ConnectionFailedException:
            self.logger.error("Failed to connect to remote host", exc_info=True)
            result_flag = False
        return result_flag

    def make_dir(self, dir_path):
        """Creates a remote directory if it does not exists yet

        Args:
            dir_path: Remote path of the directory that will be created

        Returns:
            True if path exists or the directory is successfully created, False otherwise

        Raises:
            IOError if the path exists and it is a file
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
        except SshConnection.ConnectionFailedException:
            self.logger.error("Failed to connect to remote host", exc_info=True)
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
        except SshConnection.ConnectionFailedException:
            self.logger.error("Failed to connect to remote host", exc_info=True)
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
                    self.logger.debug("DirNotFound nothing to remove", exc_info=True)
                    result_flag = True
                finally:
                    sftp_client.close()
        except SshConnection.ConnectionFailedException:
            self.logger.error("Failed to connect to remote host", exc_info=True)
            result_flag = False
        return result_flag

    def test_connection(self):
        try:
            with self.ssh_client():
                return True
        except SshConnection.ConnectionFailedException:
            self.logger.error("Failed to connect to remote host", exc_info=True)
            return False
