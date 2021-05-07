from dataclasses import dataclass

from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)


@dataclass
class JobKillController:
    env: IRemoteEnvironment
    display: IDisplay
    repo: IDataRepo

    def _check_if_job_is_killable(self, job_id):
        return self.repo.is_job_id_inside_database(job_id)

    def kill_job(self, job_id: int):
        """Kills a slurm job

        Args:
            job_id: The ID of the slurm job to be killed
        """
        if self._check_if_job_is_killable(job_id):
            self.display.show_message(
                f"Killing job {job_id}", __name__ + "." + __class__.__name__
            )
            self.env.kill_remote_job(job_id)
        else:
            self.display.show_message(
                f"You are not authorized to kill job {job_id}",
                __name__ + "." + __class__.__name__,
            )
