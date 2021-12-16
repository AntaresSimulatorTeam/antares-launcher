from abc import ABC, abstractmethod


class IConnection(ABC):
    """Main class for Connection"""

    def __init__(self):
        self.host = None
        self.username = None
        self.__home_dir = None

    @property
    def home_dir(self):
        """

        Returns: the home directory of the remote server
        """
        return self.__home_dir

    @abstractmethod
    def execute_command(self, command):
        """Execute a command on the remote host
        put stderr and stout in self.error and self.output respectively

        Args:
            command: bash command

        Returns:
            result_flag: A boolean indicating if the execution is successful or not
        """

        raise NotImplementedError

    @abstractmethod
    def upload_file(self, src, dst):
        """Uploads the file to remote server
        from self.upload_local_file_path
        to  self.upload_remote_file_path

        Args:
            src: Path of the file to upload
            dst: Destination directory
        """
        raise NotImplementedError

    @abstractmethod
    def download_file(self, src, dst):
        """This method downloads the file from remote server
        from self.download_remote_file_path
        to self.download_local_file_path

        Args:
            src: Path of the file to download
            dst: Destination directory
        """
        raise NotImplementedError

    @abstractmethod
    def check_remote_dir_exists(self, dir_path):
        """Checks if the remote path is a directory

        Args:
            dir_path: Remote path

        Returns:
            A boolean indicating if the remote directory exists or not

        Raises:
            IOError: If the path exists and is a file
        """
        raise NotImplementedError

    @abstractmethod
    def check_file_not_empty(self, file_path):
        """Checks if a remote file exists and is not empty

        Args:
            file_path: The path on the remote server

        Returns:
            A boolean True if the file exists and is not empty, False otherwise

        Raises:
            IOError: if path exists and is a directory
        """
        raise NotImplementedError

    @abstractmethod
    def make_dir(self, dir_path):
        """Creates a remote directory if it does not exists yet

        Args:
            dir_path: Remote path of the directory that needs to be created

        Returns:
            True if path exists or the directory is successfully created, False if a connection error was risen

        Raises:
            IOError: If the path exists and is a file
        """
        raise NotImplementedError

    @abstractmethod
    def remove_file(self, file_path):
        """Deletes a remote file

        Args:
            file_path: Path on the remote server

        Returns:
            True if file is successfully removed, False if file is not found

        Raises:
            IOError: If path exists and it is a directory
        """
        raise NotImplementedError

    @abstractmethod
    def remove_dir(self, dir_path):
        """Removes a remote directory

        Args:
            dir_path: Path on the remote server

        Returns:
            True if directory is successfully removed, False if file is not found

        Raises:
            IOError: If path exists and it is a directory
        """
        raise NotImplementedError

    @abstractmethod
    def test_connection(self):
        """Tests the sst connection

        Returns:
            True if the desired connection can be established, false otherwise
        """
        raise NotImplementedError
