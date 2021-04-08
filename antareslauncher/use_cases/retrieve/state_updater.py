from pathlib import Path
from typing import List

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.study_dto import StudyDTO


class StateUpdater:
    def __init__(
        self,
        env: iremote_environment.IRemoteEnvironment,
        display: IDisplay,
    ):

        self._env = env
        self._display = display
        self._current_study: StudyDTO = None

    def _show_job_state_message(self, study: StudyDTO):
        if study.done is True:
            self._display.show_message(
                f'"{Path(study.path).name}"  (JOBID={study.job_id}): everything is done',
                __name__ + "." + __class__.__name__,
            )
        else:
            if study.job_id:
                self._display.show_message(
                    f'"{Path(study.path).name}"  (JOBID={study.job_id}): {study.job_state}',
                    __name__ + "." + __class__.__name__,
                )
            else:
                self._display.show_error(
                    f'"{Path(study.path).name}": Job was not submitted',
                    __name__ + "." + __class__.__name__,
                )

    def run(self, study: StudyDTO) -> StudyDTO:
        """Gets the job state flags from the environment and update the IStudyDTO flags then save study

        Args:
            study: The study data transfer object
        """
        self._current_study = study
        if not self._current_study.done:
            self._set_current_study_job_state_flags()
            self._set_current_study_job_state()
        self._show_job_state_message(study)
        return study

    def _set_current_study_job_state_flags(self):
        if self._current_study.job_id:
            s, f, e = self._env.get_job_state_flags(self._current_study)
        else:
            s, f, e = False, False, False
        self._current_study.started = s
        self._current_study.finished = f
        self._current_study.with_error = e

    def _set_current_study_job_state(self):
        if self._current_study.with_error:
            self._current_study.job_state = "Ended with error"
        elif self._current_study.finished:
            self._current_study.job_state = "Finished"
        elif self._current_study.started:
            self._current_study.job_state = "Running"
        else:
            self._current_study.job_state = "Pending"

    def run_on_list(self, study_list: List[StudyDTO]):
        message = "Checking status of the studies:"
        self._display.show_message(
            message,
            __name__ + "." + __class__.__name__,
        )
        study_list.sort(key=lambda x: x.done, reverse=True)
        for study in study_list:
            self.run(study)
