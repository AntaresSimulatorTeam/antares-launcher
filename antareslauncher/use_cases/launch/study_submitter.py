from pathlib import Path

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO

LOG_NAME = f"{__name__}.StudySubmitter"


class StudySubmitter(object):
    def __init__(self, env: RemoteEnvironmentWithSlurm, display: DisplayTerminal):
        self.env = env
        self.display = display

    def submit_job(self, study: StudyDTO) -> None:
        if study.job_id:
            self.display.show_message(f'"{Path(study.path).name}": is already submitted', LOG_NAME)
            return
        study.job_id = self.env.submit_job(study)  # may raise SubmitJobError
        if study.job_id:
            self.display.show_message(f'"{Path(study.path).name}": was submitted', LOG_NAME)
        else:
            self.display.show_error(f'"{Path(study.path).name}": was not submitted', LOG_NAME)
