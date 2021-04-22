import configparser
import json
import logging
import os
import zipfile
from pathlib import Path

from antareslauncher.display.idisplay import IDisplay


class FileManager:
    def __init__(self, display_terminal: IDisplay):
        self.logger = logging.getLogger(__name__ + "." + __class__.__name__)
        self.display = display_terminal

    def get_config_from_file(self, file_path):
        """Reads the configuration file of antares

        Args:
            file_path: Path to the configuration file

        Returns:
            The corresponding config object
        """
        self.logger.info(f"Getting config from file {file_path}")
        config_parser = configparser.ConfigParser()
        if Path(file_path).exists():
            config_parser.read(file_path)
        return config_parser

    def listdir_of(self, directory):
        """Make a list of all the folders inside a directory

        Args:
            directory: The directory that will be the root of the wanted list

        Returns:
            A list of all the folders inside a directory
        """
        self.logger.info(f"Getting directory list from path {directory}")
        list_dir = os.listdir(directory)
        list_dir.sort()
        return list_dir

    @staticmethod
    def is_dir(dir_path: Path):
        return Path(dir_path).is_dir()

    def _get_list_dir_without_subdir(self, dir_path, subdir_to_exclude):
        """Make a list of all the folders inside a directory except one

        Args:
            dir_path: The directory that will be the root of the wanted list

            subdir_to_exclude:the subdir to remove from the list

        Returns:
            A list of all the folders inside a directory without subdir_to_exclude
        """
        list_dir = self.listdir_of(dir_path)
        if subdir_to_exclude in list_dir:
            list_dir.remove(subdir_to_exclude)
        return list_dir

    def _get_list_of_files_recursively(self, element_path):
        """Make a list of all the files inside a directory recursively

        Args:
            element_path: Root dir of the list of files

        Returns:
            List of all the files inside a directory recursively
        """
        self.logger.info(
            f"Getting list of all files inside the directory {element_path}"
        )
        element_file_paths = []
        for root, _, files in os.walk(element_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                element_file_paths.append(file_path)
        return element_file_paths

    def _get_complete_list_of_files_and_dirs_in_list_dir(self, dir_path, list_dir):
        file_paths = []
        for element in list_dir:
            element_path = os.path.join(dir_path, element)
            file_paths.append(element_path)
            if os.path.isdir(element_path):
                element_file_paths = self._get_list_of_files_recursively(element_path)
                file_paths.extend(element_file_paths)
        return file_paths

    def zip_file_paths_with_rootdir_to_zipfile_path(
        self, zipfile_path, file_paths, root_dir
    ):
        """Zips all the files in file_paths inside zipfile_path
        while printing a progress bar on the terminal

        Args:
            zipfile_path: Path of the zipfile that will be created

            file_paths: Paths of all the files that need to be zipped

            root_dir: Root directory
        """
        self.logger.info(f"Zipping list of files to archive {zipfile_path}")
        with zipfile.ZipFile(
            zipfile_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as my_zip:
            loading_bar = self.display.generate_progress_bar(
                file_paths, desc="Compressing files: "
            )
            for f in loading_bar:
                my_zip.write(f, os.path.relpath(f, root_dir))

    def zip_dir_excluding_subdir(self, dir_path, zipfile_path, subdir_to_exclude):
        """Zips a whole directory without one subdir

        Args:
            dir_path: Path of the directory to zip

            zipfile_path: Path of the zip file that will be created

            subdir_to_exclude: Subdirectory that will not be zipped
        """
        list_dir = self._get_list_dir_without_subdir(dir_path, subdir_to_exclude)
        file_paths = self._get_complete_list_of_files_and_dirs_in_list_dir(
            dir_path, list_dir
        )
        root_dir = str(Path(dir_path).parent)
        self.zip_file_paths_with_rootdir_to_zipfile_path(
            zipfile_path, file_paths, root_dir
        )
        return Path(zipfile_path).is_file()

    def unzip(self, file_path: str):
        """Unzips the result of the antares job once is has been downloaded

        Args:
            file_path: The path to the file

        Returns:
            True if the file has been extracted, False otherwise
        """
        self.logger.info(f"Unzipping {file_path}")
        try:
            with zipfile.ZipFile(file=file_path) as zip_file:
                progress_bar = self.display.generate_progress_bar(
                    zip_file.namelist(),
                    desc="Extracting archive:",
                    total=len(zip_file.namelist()),
                )
                for file in progress_bar:
                    zip_file.extract(
                        member=file,
                        path=Path(file_path).parent,
                    )
            return True
        except ValueError:
            return False
        except FileNotFoundError:
            return False

    def make_dir(self, directory_name):
        self.logger.info(f"Creating directory {directory_name}")
        os.makedirs(directory_name, exist_ok=True)

    def convert_json_file_to_dict(self, file_path):
        self.logger.info(f"Converting json file {file_path} to dict")
        try:
            with open(file_path, "r") as readFile:
                config = json.load(readFile)
        except OSError:
            self.logger.error(
                f"Unable to convert {file_path} to json (file not found or invalid type)"
            )
            config = None
        return config

    def remove_file(self, file_path: str):
        """
        Given a file path, it removes it

        Args:
            file_path: File path

        Returns: None
        """
        try:
            Path(file_path).unlink()
            self.logger.info(f"file: {file_path} got deleted")
        except FileNotFoundError:
            self.logger.warning(f"Could not find path: {str(file_path)}")

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Checks if the given file path, is a regular file

        Args:
            file_path: file_path

        Returns:
            file path, is a regular file
        """
        return Path(file_path).is_file()
