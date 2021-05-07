from dataclasses import dataclass

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)


@dataclass
class SlurmQueueShow:
    env: IRemoteEnvironment
    display: IDisplay

    def run(self):
        """Displays all the jobs un the slurm queue"""
        message = "Checking remote server queue\n" + self.env.get_queue_info()
        self.display.show_message(message, __name__ + "." + __class__.__name__)
