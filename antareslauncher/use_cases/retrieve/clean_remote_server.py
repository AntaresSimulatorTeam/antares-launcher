from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO

LOG_NAME = f"{__name__}.RemoteServerCleaner"


class RemoteServerCleaner:
    def __init__(
        self,
        env: RemoteEnvironmentWithSlurm,
        display: DisplayTerminal,
    ):
        self._display = display
        self._env = env

    def clean(self, study: StudyDTO):
        if not study.remote_server_is_clean and study.local_final_zipfile_path:
            # If the cleanup procedure fails to remove remote files or
            # delete the final ZIP, there's no need to raise an exception.
            # Instead, it's sufficient to issue a warning to alert the user.
            try:
                removed = self._env.clean_remote_server(study)
            except Exception as exc:
                self._display.show_error(
                    f'"{study.name}": Clean remote server raised: {exc}',
                    LOG_NAME,
                )
            else:
                if removed:
                    self._display.show_message(
                        f'"{study.name}": Clean remote server finished',
                        LOG_NAME,
                    )
                else:
                    self._display.show_error(
                        f'"{study.name}": Clean remote server failed',
                        LOG_NAME,
                    )

            # However, in such cases, it's advisable to indicate that the cleanup
            # was successful to prevent an infinite loop.
            study.remote_server_is_clean = True
