import copy
from pathlib import Path

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.study_dto import StudyDTO


class RemoteServerNotCleanException(Exception):
    pass


class RemoteServerCleaner:
    def __init__(
        self,
        env: iremote_environment.IRemoteEnvironment,
        display: IDisplay,
    ):
        self._display = display
        self._env = env
        self._current_study: StudyDTO = None

    def clean(self, study: StudyDTO):
        self._current_study = copy.copy(study)
        if self._should_clean_remote_server():
            self._do_clean_remote_server()
        return self._current_study

    def _should_clean_remote_server(self):
        return (
            self._current_study.remote_server_is_clean is False
        ) and self._final_zip_downloaded()

    def _final_zip_downloaded(self) -> bool:
        if isinstance(self._current_study.local_final_zipfile_path, str):
            return bool(self._current_study.local_final_zipfile_path)
        else:
            return False

    def _do_clean_remote_server(self):
        success = self._env.clean_remote_server(copy.copy(self._current_study))
        if success is True:
            self._current_study.remote_server_is_clean = success
            self._display_success_message()
        else:
            self._display_failure_error()
            raise RemoteServerNotCleanException

    def _display_failure_error(self):
        self._display.show_error(
            f'"{Path(self._current_study.path).name}": Clean remote server failed',
            __name__ + "." + __class__.__name__,
        )

    def _display_success_message(self):
        self._display.show_message(
            f'"{Path(self._current_study.path).name}": Clean remote server finished',
            __name__ + "." + __class__.__name__,
        )
