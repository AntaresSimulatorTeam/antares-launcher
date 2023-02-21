import copy
from pathlib import Path

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.study_dto import StudyDTO


class LogDownloader:
    def __init__(
        self,
        env: iremote_environment.IRemoteEnvironment,
        file_manager: FileManager,
        display: IDisplay,
    ):
        self.env = env
        self.display = display
        self.file_manager = file_manager
        self._current_study = None

    def _create_logs_subdirectory(self):
        self._set_current_study_log_dir_path()
        self.file_manager.make_dir(self._current_study.job_log_dir)

    def _set_current_study_log_dir_path(self):
        directory_name = self._get_log_dir_name()
        if Path(self._current_study.job_log_dir).name != directory_name:
            self._current_study.job_log_dir = str(
                Path(self._current_study.job_log_dir) / directory_name
            )

    def _get_log_dir_name(self):
        return (
            Path(self._current_study.path).name + "_" + str(self._current_study.job_id)
        )

    def run(self, study: StudyDTO):
        """Downloads slurm logs from the server then save study if the study is running

        Args:
            study: The study data transfer object
        """
        self._current_study = copy.copy(study)
        if self._current_study.started:
            self._create_logs_subdirectory()
            self._do_download_logs()
        return self._current_study

    def _do_download_logs(self):
        if self.env.download_logs(copy.copy(self._current_study)):
            self._current_study.logs_downloaded = True
            self.display.show_message(
                f'"{Path(self._current_study.path).name}": Logs downloaded',
                f"{__name__}.{__class__.__name__}",
            )
        else:
            self.display.show_error(
                f'"{Path(self._current_study.path).name}": Logs not downloaded',
                f"{__name__}.{__class__.__name__}",
            )
