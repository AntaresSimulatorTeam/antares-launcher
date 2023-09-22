from pathlib import Path

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO

LOG_NAME = f"{__name__}.LogDownloader"


class LogDownloader:
    def __init__(
        self,
        env: RemoteEnvironmentWithSlurm,
        display: DisplayTerminal,
    ):
        self.env = env
        self.display = display

    def run(self, study: StudyDTO) -> None:
        """
        Downloads slurm logs from the server then save study if the study is running

        Args:
            study: The study data transfer object
        """
        if study.started:
            # set_current_study_log_dir_path
            directory_name = f"{study.name}_{study.job_id}"
            job_log_dir = Path(study.job_log_dir)
            if job_log_dir.name != directory_name:
                job_log_dir = job_log_dir / directory_name
                study.job_log_dir = str(job_log_dir)

            # create logs subdirectory
            job_log_dir.mkdir(parents=True, exist_ok=True)

            # make an attempt to download logs
            downloaded_logs = self.env.download_logs(study)
            if downloaded_logs:
                study.logs_downloaded = True
                self.display.show_message(
                    f'"{study.name}": Logs downloaded',
                    LOG_NAME,
                )
            else:
                # No file to download
                self.display.show_error(
                    f'"{study.name}": Logs NOT downloaded',
                    LOG_NAME,
                )
