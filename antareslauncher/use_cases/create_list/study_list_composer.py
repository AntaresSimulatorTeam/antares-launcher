import configparser
import typing as t
from dataclasses import dataclass
from pathlib import Path

from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.study_dto import Modes, StudyDTO
from antares.study.version import SolverMinorVersion, StudyVersion

DEFAULT_VERSION = SolverMinorVersion.parse(0)

def get_solver_version(study_dir: Path, *, default: SolverMinorVersion = DEFAULT_VERSION) -> SolverMinorVersion:
    """
    Retrieve the solver version number or else the study version number
    from the "study.antares" file.

    Args:
        study_dir: Directory path which contains the "study.antares" file.
        default: Default version number to use if the version is not found.

    Returns:
        The value of `solver_version`, `version` or the default version number.
    """
    study_path = study_dir.joinpath("study.antares")
    config = configparser.ConfigParser()
    config.read(study_path)
    if "antares" not in config:
        return default
    section = config["antares"]
    for key in "solver_version", "version":
        if key in section:
            return SolverMinorVersion.parse(section[key])
    return default


@dataclass
class StudyListComposerParameters:
    studies_in_dir: str
    time_limit: int
    log_dir: str
    n_cpu: int
    xpansion_mode: str  # "", "r", "cpp"
    output_dir: str
    post_processing: bool
    antares_versions_on_remote_server: t.Sequence[SolverMinorVersion]
    other_options: str
    antares_version: SolverMinorVersion = DEFAULT_VERSION


class StudyListComposer:
    def __init__(
        self,
        repo: DataRepoTinydb,
        display: DisplayTerminal,
        parameters: StudyListComposerParameters,
    ):
        self._repo = repo
        self._display = display
        self._studies_in_dir = parameters.studies_in_dir
        self.time_limit = parameters.time_limit
        self.log_dir = parameters.log_dir
        self.n_cpu = parameters.n_cpu
        self.xpansion_mode = parameters.xpansion_mode
        self.output_dir = parameters.output_dir
        self.post_processing = parameters.post_processing
        self.other_options = parameters.other_options
        self.antares_version = parameters.antares_version
        self._new_study_added = False
        self.DEFAULT_JOB_LOG_DIR_PATH = str(Path(self.log_dir) / "JOB_LOGS")
        self.ANTARES_VERSIONS_ON_REMOTE_SERVER = parameters.antares_versions_on_remote_server

    def get_list_of_studies(self):
        """Retrieve the list of studies from the repo

        Returns:
            List of all the saved studies in the repo
        """
        return self._repo.get_list_of_studies()

    def _create_study(self, path: Path, antares_version: SolverMinorVersion, xpansion_mode: str) -> StudyDTO:
        run_mode = {
            "": Modes.antares,
            "r": Modes.xpansion_r,
            "cpp": Modes.xpansion_cpp,
        }.get(self.xpansion_mode, Modes.antares)
        new_study = StudyDTO(
            path=str(path),
            n_cpu=self.n_cpu,
            time_limit=self.time_limit,
            antares_version=StudyVersion.parse(antares_version),
            job_log_dir=self.DEFAULT_JOB_LOG_DIR_PATH,
            output_dir=str(self.output_dir),
            xpansion_mode=xpansion_mode,
            run_mode=run_mode,
            post_processing=self.post_processing,
            other_options=self.other_options,
        )
        return new_study

    def update_study_database(self):
        """List all directories inside the STUDIES_IN_DIR folder, if a directory is a valid antares study
        and is new, then creates a StudyDTO object then saves it in the repo
        """
        message = f"Updating current database from '{self._studies_in_dir}'..."
        if self.xpansion_mode:
            message += f"New studies will be run in xpansion mode {self.xpansion_mode}"
        self._display.show_message(message, f"{__name__}.{__class__.__name__}")

        self._new_study_added = False

        directories = Path(self._studies_in_dir).iterdir()
        for directory_path in sorted(directories):
            if directory_path.is_dir():
                self._update_database_with_directory(directory_path)

        if not self._new_study_added:
            self._display.show_message(
                "Didn't find any new simulations...",
                f"{__name__}.{__class__.__name__}",
            )

    def _update_database_with_directory(self, directory_path: Path):
        solver_version = get_solver_version(directory_path)
        antares_version = self.antares_version if self.antares_version != DEFAULT_VERSION else solver_version
        if not antares_version:
            self._display.show_message(
                "... not a valid Antares study",
                __name__ + "." + self.__class__.__name__,
            )
        elif antares_version not in self.ANTARES_VERSIONS_ON_REMOTE_SERVER:
            message = (
                f"... Antares version {antares_version} is not supported"
                f" (supported versions: {self.ANTARES_VERSIONS_ON_REMOTE_SERVER})"
            )
            self._display.show_message(
                message,
                __name__ + "." + self.__class__.__name__,
            )
        else:
            candidates_file_path = directory_path.joinpath("user", "expansion", "candidates.ini")
            is_xpansion_study = candidates_file_path.is_file()
            xpansion_mode = self.xpansion_mode if is_xpansion_study else ""

            valid_xpansion_candidate = self.xpansion_mode in ["r", "cpp"] and is_xpansion_study
            valid_antares_candidate = not self.xpansion_mode

            if valid_antares_candidate or valid_xpansion_candidate:
                buffer_study = self._create_study(directory_path, antares_version, xpansion_mode)
                if not self._repo.is_study_inside_database(buffer_study):
                    self._add_study_to_database(buffer_study)

    def _add_study_to_database(self, buffer_study):
        self._repo.save_study(buffer_study)
        self._display.show_message(
            f"New study added "
            f"(mode = {buffer_study.run_mode.name}, "
            f"version={buffer_study.antares_version}): "
            f'"{buffer_study.path}"',
            __name__ + "." + self.__class__.__name__,
        )
        self._new_study_added = True
