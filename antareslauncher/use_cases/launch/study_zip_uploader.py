import copy
from pathlib import Path

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import (
    RemoteEnvironmentWithSlurm,
)
from antareslauncher.study_dto import StudyDTO


class StudyZipfileUploader:
    def __init__(self, env: RemoteEnvironmentWithSlurm, display: DisplayTerminal):
        self.env = env
        self.display = display
        self._current_study: StudyDTO = None

    def upload(self, study) -> StudyDTO:
        self._current_study = copy.deepcopy(study)
        if self._current_study.zip_is_sent is False:
            self._do_upload()
        return self._current_study

    def _do_upload(self):
        self._display_welcome_message()
        success = self.env.upload_file(self._current_study.zipfile_path)
        if success:
            self._current_study.zip_is_sent = True
            self._display_success_message()
        else:
            self._display_failure_error()
            raise FailedUploadException

    def _display_failure_error(self):
        self.display.show_error(
            f'"{Path(self._current_study.path).name}": was not uploaded',
            __name__ + "." + __class__.__name__,
        )

    def _display_success_message(self):
        self.display.show_message(
            f'"{Path(self._current_study.path).name}": was uploaded',
            __name__ + "." + __class__.__name__,
        )

    def _display_welcome_message(self):
        self.display.show_message(
            f'"{Path(self._current_study.path).name}": uploading study ...',
            __name__ + "." + __class__.__name__,
        )


class FailedUploadException(Exception):
    pass
