from dataclasses import dataclass
from pathlib import Path

from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.definitions import ANTARES_VERSIONS_ON_REMOTE_SERVER
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.study_dto import StudyDTO, Modes


@dataclass
class StudyListComposer:
    repo: IDataRepo
    file_manager: FileManager
    display: IDisplay
    studies_in_dir: str
    time_limit: int
    log_dir: str
    n_cpu: int
    xpansion_mode: bool
    output_dir: str
    post_processing: bool
    # supported_antares_versions: List[str]

    def __post_init__(self):
        self.new_study_added = False
        self.DEFAULT_JOB_LOG_DIR_PATH = str(Path(self.log_dir) / "JOB_LOGS")

    def get_list_of_studies(self):
        """Retrieve the list of studies from the repo

        Returns:
            List of all the saved studies in the repo
        """
        return self.repo.get_list_of_studies()

    def get_dir_list_of_studiesin_dir(self):
        """Retrieve the list of directories inside the STUDIES_IN_DIR folder

        Returns:
            list of directories inside the STUDIES_IN_DIR folder
        """
        return self.file_manager.listdir_of(self.studies_in_dir)

    def _create_study(self, path, antares_version, xpansion_study):
        """Generate a study dto from study directory path, antares version and directory hash

        Args:
            path: path of the study directory
            antares_version: version number of antares

        Returns:
            study dto filled with the specified data
        """
        if self.xpansion_mode:
            run_mode = Modes.xpansion
        else:
            run_mode = Modes.antares

        new_study = StudyDTO(
            path=str(path),
            n_cpu=self.n_cpu,
            time_limit=self.time_limit,
            antares_version=antares_version,
            job_log_dir=self.DEFAULT_JOB_LOG_DIR_PATH,
            output_dir=str(self.output_dir),
            xpansion_study=xpansion_study,
            run_mode=run_mode,
            post_processing=self.post_processing,
        )

        return new_study

    def get_antares_version(self, directory_path: str):
        """Checks if the directory is an antares study and returns the version

        Checks if the directory is an antares study by checking the presence of the study.antares file
        and by checking the presence of the 'antares' field in this file.

        Args:
            directory_path: Path of the directory to test

        Returns:
            The version if the directory is an antares study, None otherwise
        """
        file_path = Path(directory_path) / "study.antares"
        config = self.file_manager.get_config_from_file(file_path)
        if "antares" in config:
            return config["antares"].get("version", None)

    def _is_valid_antares_study(self, antares_version):
        """Checks if antares version is a positive number compatible with version
        installed on the remote server (the list is found in the definitions

        Args:
            antares_version: antares version

        Returns:
            True if the version is positive, False otherwise
        """
        if antares_version is None:
            self.display.show_message(
                "... not a valid Antares study",
                __name__ + "." + __class__.__name__,
            )
            return False

        elif antares_version in ANTARES_VERSIONS_ON_REMOTE_SERVER:
            return True
        else:
            message = f"... Antares version ({antares_version}) is not supported (supported versions: {ANTARES_VERSIONS_ON_REMOTE_SERVER})"
            self.display.show_message(
                message,
                __name__ + "." + __class__.__name__,
            )
            return False

    def _is_there_candidates_file(self, directory_path: Path):
        """Checks if the file candidates.ini exists

        Args:
            directory_path: path to the study

        Returns:
            True if candidates.ini exists, False otherwise
        """
        candidates_file_path = str(
            Path.joinpath(directory_path, "user", "expansion", "candidates.ini")
        )
        return self.file_manager.file_exists(candidates_file_path)

    def _is_xpansion_study(self, xpansion_study_path: str):
        """Checks if the study correspond to an xpansion study

        Args:
            xpansion_study_path: path to the study

        Returns:
            True if the directory correspond to an xpansion study, False otherwise
        """
        return self._is_there_candidates_file(Path(xpansion_study_path))

    def update_study_database(self):
        """List all directories inside the STUDIES_IN_DIR folder, if a directory is a valid antares study
        and is new, then creates an IStudyDTO object then saves it in the repo
        """
        if self.xpansion_mode:
            message = (
                "Updating current database... New studies will be ran in xpansion mode"
            )
        else:
            message = "Updating current database..."

        self.display.show_message(
            message,
            __name__ + "." + __class__.__name__,
        )

        self.new_study_added = False
        for directory in self.get_dir_list_of_studiesin_dir():
            directory_path = str(Path(self.studies_in_dir) / Path(directory))
            if self.file_manager.is_dir(Path(directory_path)):
                self._update_database_with_directory(directory_path)

        if not self.new_study_added:
            self.display.show_message(
                "Didn't find any new simulations...",
                __name__ + "." + __class__.__name__,
            )

    def _update_database_with_new_study(
        self, antares_version, directory_path, is_xpansion_study
    ):
        buffer_study = self._create_study(
            directory_path, antares_version, is_xpansion_study
        )
        self._update_database_with_study(buffer_study)

    def _update_database_with_directory(self, directory_path):
        antares_version = self.get_antares_version(directory_path)
        if self._is_valid_antares_study(antares_version):
            is_xpansion_study = self._is_xpansion_study(directory_path)

            valid_xpansion_candidate = self.xpansion_mode and is_xpansion_study
            valid_antares_candidate = not self.xpansion_mode

            if valid_antares_candidate or valid_xpansion_candidate:
                self._update_database_with_new_study(
                    antares_version, directory_path, is_xpansion_study
                )

    def _update_database_with_study(self, buffer_study):
        if not self.repo.is_study_inside_database(buffer_study):
            self._add_study_to_database(buffer_study)

    def _add_study_to_database(self, buffer_study):
        self.repo.save_study(buffer_study)
        self._display.show_message(
            f"New study added "
            f"(mode = {buffer_study.run_mode.name}, "
            f"version={buffer_study.antares_version}): "
            f'"{buffer_study.path}"',
            __name__ + "." + __class__.__name__,
        )
        self.new_study_added = True
