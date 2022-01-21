from dataclasses import dataclass
from typing import Optional

from antareslauncher.use_cases.check_remote_queue.check_queue_controller import (
    CheckQueueController,
)
from antareslauncher.use_cases.create_list.study_list_composer import (
    StudyListComposer,
)
from antareslauncher.use_cases.kill_job.job_kill_controller import (
    JobKillController,
)
from antareslauncher.use_cases.launch.launch_controller import LaunchController
from antareslauncher.use_cases.retrieve.retrieve_controller import (
    RetrieveController,
)
from antareslauncher.use_cases.wait_loop_controller.wait_controller import (
    WaitController,
)


@dataclass
class AntaresLauncher:
    study_list_composer: StudyListComposer
    launch_controller: LaunchController
    retrieve_controller: RetrieveController
    job_kill_controller: JobKillController
    check_queue_controller: CheckQueueController
    wait_controller: WaitController
    wait_mode: bool
    wait_time: int
    xpansion_mode: Optional[str]
    check_queue_bool: bool
    job_id_to_kill: Optional[int] = None

    def run_once_mode(self):
        """Runs antares_launcher only once:
        update the database with the new studies found in the input directory
        submit all new studies
        retrieve all the finished studies.
        The code exit even if there are still unfinished jobs
        """
        self.study_list_composer.update_study_database()
        self.launch_controller.launch_all_studies()
        self.retrieve_controller.retrieve_all_studies()

    def run_wait_mode(self):
        """Run antares_launcher once then it keeps
        checking the status of the unfinished jobs until all jobs are finished,
        The code exit when all job are finished the the results are retrieved and extracted
        """
        self.run_once_mode()
        while not self.retrieve_controller.all_studies_done:
            self.wait_controller.countdown(seconds_to_wait=self.wait_time)
            self.retrieve_controller.retrieve_all_studies()

    def run(self):
        """Use the options to decide which action to perform"""
        if self.job_id_to_kill:
            self.job_kill_controller.kill_job(self.job_id_to_kill)
        elif self.check_queue_bool:
            self.check_queue_controller.check_queue()
        elif self.wait_mode:
            self.run_wait_mode()
        else:
            self.run_once_mode()
