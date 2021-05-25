import copy
from pathlib import Path

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)
from antareslauncher.study_dto import StudyDTO


class FailedSubmissionException(Exception):
    pass


class StudySubmitter(object):
    def __init__(self, env: IRemoteEnvironment, display: IDisplay):
        self.env = env
        self.display = display
        self._current_study: StudyDTO = None

    def submit_job(self, study: StudyDTO) -> StudyDTO:
        self._current_study = copy.deepcopy(study)
        if self._current_study.job_id is None:
            self._do_submit()
        return self._current_study

    def _do_submit(self):
        job_id = self.env.submit_job(copy.deepcopy(self._current_study))
        if job_id is not None:
            self._current_study.job_id = job_id
            self.display.show_message(
                f'"{Path(self._current_study.path).name}": was submitted',
                __name__ + "." + __class__.__name__,
            )
        else:
            self.display.show_error(
                f'"{Path(self._current_study.path).name}": was not submitted',
                __name__ + "." + __class__.__name__,
            )
            raise FailedSubmissionException
