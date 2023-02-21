from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.study_dto import StudyDTO, Modes


@dataclass
class StudyListComposerParameters:
    studies_in_dir: str
    time_limit: int
    log_dir: str
    n_cpu: int
    xpansion_mode: Optional[str]
    output_dir: str
    post_processing: bool
    antares_versions_on_remote_server: List[str]
    other_options: str


@dataclass
class StudyListComposer:
    def __init__(
        self,
        repo: IDataRepo,
        file_manager: FileManager,
        display: IDisplay,
        parameters: StudyListComposerParameters,
    ):
        self._repo = repo
        self._file_manager = file_manager
        self._display = display
        self._studies_in_dir = parameters.studies_in_dir
        self.time_limit = parameters.time_limit
        self.log_dir = parameters.log_dir
        self.n_cpu = parameters.n_cpu
        self.xpansion_mode = parameters.xpansion_mode
        self.output_dir = parameters.output_dir
        self.post_processing = parameters.post_processing
        self.other_options = parameters.other_options
        self._new_study_added = False
        self.DEFAULT_JOB_LOG_DIR_PATH = str(Path(self.log_dir) / "JOB_LOGS")
        self.ANTARES_VERSIONS_ON_REMOTE_SERVER = (
            parameters.antares_versions_on_remote_server
        )

    def get_list_of_studies(self):
        """Retrieve the list of studies from the repo

        Returns:
            List of all the saved studies in the repo
        """
        return self._repo.get_list_of_studies()

    def _create_study(self, path, antares_version, xpansion_mode: str):
        if self.xpansion_mode == "r":
            run_mode = Modes.xpansion_r
        elif self.xpansion_mode == "cpp":
            run_mode = Modes.xpansion_cpp
        else:
            run_mode = Modes.antares

        new_study = StudyDTO(
            path=str(path),
            n_cpu=self.n_cpu,
            time_limit=self.time_limit,
            antares_version=antares_version,
            job_log_dir=self.DEFAULT_JOB_LOG_DIR_PATH,
            output_dir=str(self.output_dir),
            xpansion_mode=xpansion_mode,
            run_mode=run_mode,
            post_processing=self.post_processing,
            other_options=self.other_options,
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
        config = self._file_manager.get_config_from_file(file_path)
        if "antares" in config:
            solver_version = config["antares"].get("solver_version", None)
            return solver_version or config["antares"].get("version", None)

    def _is_valid_antares_study(self, antares_version):
        if antares_version is None:
            self._display.show_message(
                "... not a valid Antares study",
                __name__ + "." + __class__.__name__,
            )
            return False

        elif antares_version in self.ANTARES_VERSIONS_ON_REMOTE_SERVER:
            return True
        else:
            message = f"... Antares version ({antares_version}) is not supported (supported versions: {self.ANTARES_VERSIONS_ON_REMOTE_SERVER})"
            self._display.show_message(
                message,
                __name__ + "." + __class__.__name__,
            )
            return False

    def _is_there_candidates_file(self, directory_path: Path):
        candidates_file_path = str(
            Path.joinpath(directory_path, "user", "expansion", "candidates.ini")
        )
        return self._file_manager.file_exists(candidates_file_path)

    def _is_xpansion_study(self, xpansion_study_path: str):
        return self._is_there_candidates_file(Path(xpansion_study_path))

    def update_study_database(self):
        """List all directories inside the STUDIES_IN_DIR folder, if a directory is a valid antares study
        and is new, then creates a StudyDTO object then saves it in the repo
        """
        message = f"Updating current database from '{self._studies_in_dir}'..."
        if self.xpansion_mode:
            message += f"New studies will be run in xpansion mode {self.xpansion_mode}"
        self._display.show_message(message, f"{__name__}.{__class__.__name__}")

        self._new_study_added = False

        directories = self._file_manager.listdir_of(self._studies_in_dir)
        for directory in directories:
            directory_path = Path(self._studies_in_dir) / Path(directory)
            if self._file_manager.is_dir(directory_path):
                self._update_database_with_directory(directory_path)

        if not self._new_study_added:
            self._display.show_message(
                "Didn't find any new simulations...",
                f"{__name__}.{__class__.__name__}",
            )

    def _update_database_with_new_study(
        self, antares_version, directory_path, xpansion_mode: str
    ):
        buffer_study = self._create_study(
            directory_path, antares_version, xpansion_mode
        )
        self._update_database_with_study(buffer_study)

    def _update_database_with_directory(self, directory_path):
        antares_version = self.get_antares_version(directory_path)
        if self._is_valid_antares_study(antares_version):
            is_xpansion_study = self._is_xpansion_study(directory_path)
            xpansion_mode = self.xpansion_mode if is_xpansion_study else None

            valid_xpansion_candidate = (
                self.xpansion_mode in ["r", "cpp"] and is_xpansion_study
            )
            valid_antares_candidate = self.xpansion_mode is None

            if valid_antares_candidate or valid_xpansion_candidate:
                self._update_database_with_new_study(
                    antares_version, directory_path, xpansion_mode
                )

    def _update_database_with_study(self, buffer_study):
        if not self._repo.is_study_inside_database(buffer_study):
            self._add_study_to_database(buffer_study)

    def _add_study_to_database(self, buffer_study):
        self._repo.save_study(buffer_study)
        self._display.show_message(
            f"New study added "
            f"(mode = {buffer_study.run_mode.name}, "
            f"version={buffer_study.antares_version}): "
            f'"{buffer_study.path}"',
            __name__ + "." + __class__.__name__,
        )
        self._new_study_added = True
