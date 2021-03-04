from abc import ABC, abstractmethod

from antareslauncher.remote_environnement import iconnection
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
    pass


class KillJobErrorException(Exception):
    pass


class SubmitJobErrorException(Exception):
    pass


class GetJobStateOutputException(Exception):
    pass


class IRemoteEnvironment(ABC):
    """Class that represents the remote environment"""

    def __init__(self, _connection: iconnection.IConnection):
        self.connection = _connection
        self.remote_base_path = None

    @abstractmethod
    def get_queue_info(self):
        raise NotImplementedError

    @abstractmethod
    def kill_remote_job(self, job_id):
        raise NotImplementedError

    @abstractmethod
    def compose_command_to_check_state(self, job_id):
        raise NotImplementedError

    @abstractmethod
    def check_job_state(self, arg_study: StudyDTO):
        raise NotImplementedError

    @abstractmethod
    def upload_file(self, src):
        raise NotImplementedError

    @abstractmethod
    def download_logs(self, study: StudyDTO):
        raise NotImplementedError

    @abstractmethod
    def download_final_zip(self, study: StudyDTO) -> str:
        raise NotImplementedError

    @abstractmethod
    def clean_remote_server(self, study: StudyDTO) -> bool:
        raise NotImplementedError

    def execute_command(self, cmd):
        return self.connection.execute_command(cmd)

    def check_file_not_empty(self, file_path):
        return self.connection.check_file_not_empty(file_path)

    @abstractmethod
    def submit_job(self, _study: StudyDTO):
        raise NotImplementedError

    @abstractmethod
    def get_job_state_flags(self, _study: StudyDTO) -> [bool, bool, bool]:
        raise NotImplementedError
