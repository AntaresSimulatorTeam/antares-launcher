from dataclasses import dataclass

from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.use_cases.check_remote_queue.slurm_queue_show import (
    SlurmQueueShow,
)
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater


@dataclass
class CheckQueueController:
    slurm_queue_show: SlurmQueueShow
    state_updater: StateUpdater
    repo: IDataRepo

    def check_queue(self):
        """Displays all the jobs un the slurm queue"""
        self.slurm_queue_show.run()

        studies = self.repo.get_list_of_studies()
        self.state_updater.run_on_list(studies)
