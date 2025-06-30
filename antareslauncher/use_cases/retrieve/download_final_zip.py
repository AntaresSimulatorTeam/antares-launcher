from pathlib import Path

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO

LOG_NAME = f"{__name__}.FinalZipDownloader"


class FinalZipDownloader(object):
    def __init__(
        self,
        env: RemoteEnvironmentWithSlurm,
        display: DisplayTerminal,
    ):
        self._env = env
        self._display = display

    def download(self, study: StudyDTO):
        """
        Download the final ZIP file for the specified study if it has finished
        (without error) and has not been downloaded yet.

        Args:
            study: A data transfer object representing the study to download.

        Returns:
            The updated data transfer object, with its `local_final_zipfile_path`
            attribute set if the download was successful.
        """
        if study.finished and not study.local_final_zipfile_path:
            self._display.show_message(
                f'"{study.name}": downloading final ZIP...',
                LOG_NAME,
            )
            dst_dir = Path(study.output_dir)
            dst_dir.mkdir(parents=True, exist_ok=True)
            zip_path = self._env.download_final_zip(study)
            study.local_final_zipfile_path = str(zip_path) if zip_path else ""
            if study.local_final_zipfile_path:
                self._display.show_message(
                    f'"{study.name}": Final ZIP downloaded',
                    LOG_NAME,
                )
            else:
                self._display.show_error(
                    f'"{study.name}": Final ZIP NOT downloaded',
                    LOG_NAME,
                )
