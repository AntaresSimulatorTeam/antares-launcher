from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO

LOG_NAME = f"{__name__}.StudyZipfileUploader"


class StudyZipfileUploader:
    def __init__(self, env: RemoteEnvironmentWithSlurm, display: DisplayTerminal):
        self.env = env
        self.display = display

    def upload(self, study: StudyDTO) -> None:
        if study.zip_is_sent:
            self.display.show_message(f'"{study.name}": ZIP is already uploaded', LOG_NAME)
            return
        self.display.show_message(f'"{study.name}": uploading study...', LOG_NAME)
        study.zip_is_sent = self.env.upload_file(study.zipfile_path)
        if study.zip_is_sent:
            self.display.show_message(f'"{study.name}": was uploaded', LOG_NAME)
        else:
            self.display.show_error(f'"{study.name}": was NOT uploaded', LOG_NAME)

    def remove(self, study: StudyDTO) -> None:
        # The remote ZIP file is always removed even if `zip_is_sent` is `False`
        # because the ZIP file may be partially uploaded (before a failure).
        study.zip_is_sent = not self.env.remove_input_zipfile(study)
        if not study.zip_is_sent:
            self.display.show_message(f'"{study.name}": ZIP is removed from remote', LOG_NAME)
        else:
            self.display.show_error(f'"{study.name}": ZIP is NOT removed from remote', LOG_NAME)
