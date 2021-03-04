import logging
import socket
import stat
from os.path import expanduser

import paramiko

from antareslauncher.remote_environnement.iconnection import IConnection


class SshConnection(IConnection):
    """Class to _connect to remote server"""

    def __init__(self, config: dict = None):
        """

        Args:
            config: Dictionary containing the "hostname" (name or IP), "username", "port" (default is 22),
            "password" (not compulsory if private_key_file is given), "private_key_file": path to private rsa key
        """
        super(SshConnection, self).__init__()
        self.logger = logging.getLogger(__name__ + "." + __class__.__name__)
        self.__client = None
        self.__home_dir = None
        self.timeout = 10

        if config:
            self.logger.info("Loading ssh connection from config dictionary")
            self.__init_from_config(config)
        else:
            raise IOError
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
        self.password = config.get("password", None)
        key_password = config.get("key_password", None)
        key_file = config.get("private_key_file", None)
        if key_file:
            key_file_path = expanduser(key_file)
            self.__initialise_public_key(
                key_file_name=key_file_path, key_password=key_password
            )
        elif self.password is None:
            self.logger.debug("self.password is None")
            raise ValueError

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

    def _connect(self):
        """Opens the connection to remote server"""
        try:
            # Paramiko.SSHClient can be used to make connections to the remote server and transfer files
            self.__client = paramiko.SSHClient()
            # Parsing an instance of the AutoAddPolicy to set_missing_host_key_policy() changes it to allow any host.
            self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Connect to the server
            if self.private_key:
                self.__client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=self.private_key,
                    timeout=self.timeout,
                    allow_agent=False,
                )
                # look_for_keys=False disable searching for discoverable private key files in ~/.ssh/
            else:
                self.__client.connect(
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
            result_flag = False
        except paramiko.SSHException:
            self.logger.exception(f"paramiko.SSHException: {paramiko.SSHException}")
            result_flag = False
        except socket.timeout:
            self.logger.exception(f"socket.timeout: {socket.timeout}")
            result_flag = False
        except socket.error:
            self.logger.exception(f"socket.error: {socket.error}")
            result_flag = False
            self.__client.close()
        else:
            result_flag = True

        return result_flag

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
        error = None
        self.logger.info(f"Executing command on remote server: {command}")
        try:
            if self._connect():
                stdin, stdout, stderr = self.__client.exec_command(command, timeout=30)
                output = stdout.read().decode("utf-8")
                error = stderr.read().decode("utf-8")
                self.__client.close()
        except socket.timeout:
            error = f"Command timed out {command}"
            self.__client.close()
        except paramiko.SSHException:
            error = f"Failed to execute the {command}"
            self.__client.close()
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
            if self._connect():
                self.logger.info(f"Uploading file {src} to remote directory {dst}")
                sftp_client = self.__client.open_sftp()
                sftp_client.put(src, dst)
                sftp_client.close()
            else:
                result_flag = False
        except paramiko.SSHException:
            self.logger.debug("Paramiko SSH Exception")
            result_flag = False
        except IOError:
            self.logger.debug("IO Error")
            result_flag = False
        else:
            self.__client.close()
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
            if self._connect():
                self.logger.info(
                    f'Downloading remote file "{src}" to directory "{dst}"'
                )
                sftp_client = self.__client.open_sftp()
                sftp_client.get(src, dst)
                sftp_client.close()
                result_flag = True
            else:
                result_flag = False
        except paramiko.SSHException:
            self.logger.debug("Paramiko SSH Exception")
            result_flag = False
        else:
            self.__client.close()
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
        if self._connect():
            sftp_client = self.__client.open_sftp()
            try:
                self.logger.info(f"Checking remote dir {dir_path} exists")
                sftp_stat = sftp_client.stat(dir_path)
                if stat.S_ISDIR(sftp_stat.st_mode):
                    return True
                else:
                    raise IOError
            except FileNotFoundError:
                self.logger.debug("FileNotFoundError")
                return False
            finally:
                sftp_client.close()
        else:
            return False

    def check_file_not_empty(self, file_path):
        """Checks if a remote file exists and is not empty

        Args:
            file_path: Path on the remote server

        Returns:
            True if file exists and is not empty, False otherwise

        Raises:
            IOError if path exists and it is a directory
        """
        if self._connect():
            sftp_client = self.__client.open_sftp()
            try:
                self.logger.info(f'Checking remote file "{file_path}" not empty')
                sftp_stat = sftp_client.stat(file_path)
                if stat.S_ISREG(sftp_stat.st_mode):
                    if sftp_stat.st_size > 0:
                        return True
                    else:
                        return False
                else:
                    raise IOError
            except FileNotFoundError:
                self.logger.debug("FileNotFoundError")
                return False
            finally:
                sftp_client.close()
        else:
            return False

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
            if self._connect():
                sftp_client = self.__client.open_sftp()
                try:
                    self.logger.info(f"Checking if remote directory {dir_path} exists")
                    sftp_stat = sftp_client.stat(dir_path)
                    if stat.S_ISDIR(sftp_stat.st_mode):
                        result_flag = True
                    else:
                        result_flag = False
                except FileNotFoundError:
                    self.logger.info(f"Creating remote directory {dir_path}")
                    sftp_client.mkdir(dir_path)
                    result_flag = True
                finally:
                    sftp_client.close()
            else:
                result_flag = False
        except paramiko.SSHException:
            self.logger.debug("Paramiko SSHException")
            result_flag = False
        else:
            self.__client.close()
        return result_flag

    def remove_file(self, file_path):
        """Removes a remote file

        Args:
            file_path: Path on the remote server

        Returns:
            True if file is successfully removed, False otherwise

        Raises:
            IOError if path exists and it is a directory
        """
        if self._connect():
            sftp_client = self.__client.open_sftp()
            try:
                self.logger.info(f"Removing remote file {file_path}")
                sftp_stat = sftp_client.stat(file_path)
                if stat.S_ISREG(sftp_stat.st_mode):
                    try:
                        sftp_client.remove(file_path)
                    except IOError:
                        pass
                    return True
                else:
                    raise IOError
            except FileNotFoundError:
                self.logger.debug("FileNotFoundError")
                return True
            finally:
                sftp_client.close()
        else:
            return False

    def remove_dir(self, dir_path):
        """Removes a remote directory

        Args:
            dir_path: Path on the remote server

        Returns:
            True if the directory is successfully removed, False otherwise

        Raises:
            IOError if path exists and it is a file
        """
        if self._connect():
            sftp_client = self.__client.open_sftp()
            try:
                self.logger.info(f"Removing remote directory {dir_path}")
                sftp_stat = sftp_client.stat(dir_path)
                if stat.S_ISDIR(sftp_stat.st_mode):
                    try:
                        sftp_client.rmdir(dir_path)
                    except IOError:
                        pass
                    return True
                else:
                    raise IOError
            except FileNotFoundError:
                self.logger.debug("FileNotFoundError")
                return False
            finally:
                sftp_client.close()
        else:
            return False

    def test_connection(self):
        if self._connect():
            self.__client.close()
            return True
        return False
