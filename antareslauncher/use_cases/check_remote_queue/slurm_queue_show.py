from dataclasses import dataclass

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm


@dataclass
class SlurmQueueShow:
    env: RemoteEnvironmentWithSlurm
    display: DisplayTerminal

    def run(self):
        """Displays all the jobs un the slurm queue"""
        message = "Checking remote server queue\n" + self.env.get_queue_info()
        self.display.show_message(message, f"{__name__}.{__class__.__name__}")
