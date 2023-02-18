from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from antareslauncher.remote_environnement.ssh_connection import SshConnection
from antareslauncher.study_dto import StudyDTO

NOT_SUBMITTED_STATE = "not_submitted"
SUBMITTED_STATE = "submitted"
STARTED_STATE = "started"
FINISHED_STATE = "finished"
FINISHED_WITH_ERROR_STATE = "finished_with_error"


class GetJobStateErrorException(Exception):
    pass


class NoRemoteBaseDirException(Exception):
    pass


class NoLaunchScriptFoundException(Exception):
    def __init__(self, remote_path: str):
        msg = f"Launch script not found in remote server: '{remote_path}."
        super().__init__(msg)


class KillJobErrorException(Exception):
    pass


class SubmitJobErrorException(Exception):
    pass


class GetJobStateOutputException(Exception):
    pass


class IRemoteEnvironment(ABC):
    """Class that represents the remote environment"""

    def __init__(self, _connection: SshConnection):
        self.connection = _connection
        self.remote_base_path = None

    @abstractmethod
    def get_queue_info(self):
        raise NotImplementedError

    @abstractmethod
    def kill_remote_job(self, job_id):
        raise NotImplementedError

    @abstractmethod
    def upload_file(self, src):
        raise NotImplementedError

    @abstractmethod
    def download_logs(self, study: StudyDTO) -> List[Path]:
        raise NotImplementedError

    @abstractmethod
    def download_final_zip(self, study: StudyDTO) -> Optional[Path]:
        raise NotImplementedError

    @abstractmethod
    def clean_remote_server(self, study: StudyDTO) -> bool:
        raise NotImplementedError

    @abstractmethod
    def submit_job(self, _study: StudyDTO):
        raise NotImplementedError

    @abstractmethod
    def get_job_state_flags(self, _study: StudyDTO) -> [bool, bool, bool]:
        raise NotImplementedError
