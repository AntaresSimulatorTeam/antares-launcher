import typing as t

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO

LOG_NAME = f"{__name__}.RetrieveController"


class StateUpdater:
    def __init__(
        self,
        env: RemoteEnvironmentWithSlurm,
        display: DisplayTerminal,
    ):
        self._env = env
        self._display = display

    def _show_job_state_message(self, study: StudyDTO) -> None:
        if study.done:
            self._display.show_message(
                f'"{study.name}": (JOBID={study.job_id}): everything is done',
                LOG_NAME,
            )
        elif study.job_id:
            self._display.show_message(
                f'"{study.name}": (JOBID={study.job_id}): {study.job_state}',
                LOG_NAME,
            )
        else:
            self._display.show_error(
                f'"{study.name}": Job was NOT submitted',
                LOG_NAME,
            )

    def run(self, study: StudyDTO) -> None:
        """Gets the job state flags from the environment and update the IStudyDTO flags then save study

        Args:
            study: The study data transfer object
        """
        if not study.done and not study.with_error:
            # set current study job state flags
            if study.job_id:
                s, f, e = self._env.get_job_state_flags(study)
            else:
                s, f, e = False, False, False
            study.started = s
            study.finished = f
            study.with_error = e

        # set current study job state
        if study.with_error:
            study.job_state = "Ended with error"
        elif study.finished:
            study.job_state = "Finished"
        elif study.started:
            study.job_state = "Running"
        else:
            study.job_state = "Pending"

        self._show_job_state_message(study)

    def run_on_list(self, studies: t.Sequence[StudyDTO]) -> None:
        self._display.show_message("Checking status of the studies:", LOG_NAME)
        for study in sorted(studies, key=lambda x: x.done, reverse=True):
            self.run(study)
