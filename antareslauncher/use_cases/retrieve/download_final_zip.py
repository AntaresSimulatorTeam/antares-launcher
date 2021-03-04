import copy

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.study_dto import StudyDTO


class FinalZipNotDownloadedException(Exception):
    pass


class FinalZipDownloader(object):
    def __init__(
        self,
        env: iremote_environment.IRemoteEnvironment,
        display: IDisplay,
    ):
        self._env = env
        self._display = display
        self._current_study = None

    def download(self, study: StudyDTO):
        self._current_study = copy.copy(study)
        if self._should_download_final_zip():
            self._do_download()
        return self._current_study

    def _should_download_final_zip(self):
        return (
            self._study_successfully_finished()
            and self._study_final_zip_not_yet_downloaded()
        )

    def _study_successfully_finished(self):
        return self._current_study.finished and not self._current_study.with_error

    def _study_final_zip_not_yet_downloaded(self):
        return not self._current_study.local_final_zipfile_path

    def _do_download(self):
        self._display_welcome_message()
        local_final_zipfile_path = self._env.download_final_zip(
            copy.copy(self._current_study)
        )
        if local_final_zipfile_path:
            self._current_study.local_final_zipfile_path = local_final_zipfile_path
            self._display_success_message()
        else:
            self._display_failure_error()
            raise FinalZipNotDownloadedException

    def _display_failure_error(self):
        self._display.show_error(
            f'"{self._current_study.name}": Final zip not downloaded',
            __name__ + "." + __class__.__name__,
        )

    def _display_success_message(self):
        self._display.show_message(
            f'"{self._current_study.name}": Final zip downloaded',
            __name__ + "." + __class__.__name__,
        )

    def _display_welcome_message(self):
        self._display.show_message(
            f'"{self._current_study.name}": downloading final zip...',
            __name__ + "." + __class__.__name__,
        )
