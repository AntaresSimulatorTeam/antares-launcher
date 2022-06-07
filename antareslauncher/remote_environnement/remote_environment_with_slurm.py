import getpass
import ntpath
import socket
import time
from pathlib import Path

from antareslauncher.remote_environnement import iconnection
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
    NoRemoteBaseDirException,
    NoLaunchScriptFoundException,
    KillJobErrorException,
    SubmitJobErrorException,
    GetJobStateErrorException,
    GetJobStateOutputException,
)
from antareslauncher.remote_environnement.slurm_script_features import (
    SlurmScriptFeatures,
    ScriptParametersDTO,
)
from antareslauncher.study_dto import StudyDTO

SLURM_STATE_FAILED = "FAILED"
SLURM_STATE_TIMEOUT = "TIMEOUT"
SLURM_STATE_CANCELLED = "CANCELLED"
SLURM_STATE_COMPLETED = "COMPLETED"
SLURM_STATE_RUNNING = "RUNNING"


class RemoteEnvironmentWithSlurm(IRemoteEnvironment):
    """Class that represents the remote environment"""

    def __init__(
        self,
        _connection: iconnection.IConnection,
        slurm_script_features: SlurmScriptFeatures,
    ):
        super(RemoteEnvironmentWithSlurm, self).__init__(_connection=_connection)
        self.slurm_script_features = slurm_script_features
        self.remote_base_path: str = ""
        self._initialise_remote_path()
        self._check_remote_script()

    def _initialise_remote_path(self):
        self._set_remote_base_path()
        if not self.connection.make_dir(self.remote_base_path):
            raise NoRemoteBaseDirException

    def _set_remote_base_path(self):
        remote_home_dir = self.connection.home_dir
        self.remote_base_path = (
            str(remote_home_dir)
            + "/REMOTE_"
            + getpass.getuser()
            + "_"
            + socket.gethostname()
        )

    def _check_remote_script(self):
        remote_antares_script = self.slurm_script_features.solver_script_path
        if not self.connection.check_file_not_empty(remote_antares_script):
            raise NoLaunchScriptFoundException

    def get_queue_info(self):
        """This function return the information from: squeue -u run-antares

        Returns:
            The error if connection.execute_command raises an error, otherwise the slurm queue info
        """
        username = self.connection.username
        command = f"squeue -u {username} --Format=name:40,state:12,starttime:22,TimeUsed:12,timelimit:12"
        output, error = self.connection.execute_command(command)
        if error:
            return error
        else:
            return f"{username}@{self.connection.host}\n" + output

    def kill_remote_job(self, job_id):
        """Kills job with ID

        Args:
            job_id: Id of the job to kill

        Raises:
            KillJobErrorException if the command raises an error
        """

        command = f"scancel {job_id}"
        _, error = self.connection.execute_command(command)
        if error:
            raise KillJobErrorException

    @staticmethod
    def convert_time_limit_from_seconds_to_minutes(time_limit_seconds):
        """Converts time in seconds to time in minutes

        Args:
            time_limit_seconds: The time limit in seconds

        Returns:
            The value of the time limit in minutes
        """
        minimum_duration_in_minutes = 1
        time_limit_minutes = int(time_limit_seconds / 60)
        if time_limit_minutes < minimum_duration_in_minutes:
            time_limit_minutes = minimum_duration_in_minutes
        return time_limit_minutes

    def compose_launch_command(self, script_params: ScriptParametersDTO):
        return self.slurm_script_features.compose_launch_command(
            self.remote_base_path,
            script_params,
        )

    def submit_job(self, my_study: StudyDTO):
        """Submits the Antares job to slurm

        Args:
            my_study: The study data transfer object

        Returns:
            The slurm job id if the study has been submitted

        Raises:
            SubmitJobErrorException if the job has not been successfully submitted
        """
        time_limit = self.convert_time_limit_from_seconds_to_minutes(
            my_study.time_limit
        )
        script_params = ScriptParametersDTO(
            study_dir_name=Path(my_study.path).name,
            input_zipfile_name=Path(my_study.zipfile_path).name,
            time_limit=time_limit,
            n_cpu=my_study.n_cpu,
            antares_version=my_study.antares_version,
            run_mode=my_study.run_mode,
            post_processing=my_study.post_processing,
            other_options=my_study.other_options or ""
        )
        command = self.compose_launch_command(script_params)
        output, error = self.connection.execute_command(command)
        if error:
            raise SubmitJobErrorException
        job_id = self._get_jobid_from_output_of_submit_command(output)
        return job_id

    @staticmethod
    def _get_jobid_from_output_of_submit_command(output):
        job_id = None
        # SLURM squeue command returns f'Submitted {job_id}' if successful
        stdout_list = str(output).split()
        if stdout_list and stdout_list[0] == "Submitted":
            job_id = int(stdout_list[-1])
        return job_id

    @staticmethod
    def get_advancement_flags_from_state(state):
        """Converts the slurm state of the job to 3 boolean values

        Args:
            state: The job state string as obtained from Slurm

        Returns:
            started, finished, with_error: the booleans representing the advancement of the slurm_job
        """

        if state == SLURM_STATE_RUNNING:
            started = True
            finished = False
            with_error = False
        elif state == SLURM_STATE_COMPLETED:
            started = True
            finished = True
            with_error = False
        elif (
            state.startswith(SLURM_STATE_CANCELLED)
            or state.startswith(SLURM_STATE_TIMEOUT)
            or state == SLURM_STATE_FAILED
        ):
            started = True
            with_error = True
            finished = True
        # PENDING
        else:
            started = False
            finished = False
            with_error = False

        return started, finished, with_error

    def _check_job_state(self, job_id: int):
        """Checks the slurm state of a study

        Args:
            job_id: The id of the job to be checked

        Returns:
            The slurm job state string if the server correctly returned id

        Raises:
            GetJobStateErrorException if the job_state has not been obtained
        """
        command = self._compose_command_to_get_state_as_one_word(job_id)
        max_number_of_tries = 5
        seconds_to_wait = 0.5
        for _ in range(max_number_of_tries):
            output, error = self.connection.execute_command(command)
            if error:
                raise GetJobStateErrorException
            stdout = str(output).split()
            if stdout:
                return stdout[0]
            time.sleep(seconds_to_wait)

        raise GetJobStateOutputException

    @staticmethod
    def _compose_command_to_get_state_as_one_word(job_id):
        return (
            f"sacct -j {int(job_id)} -n --format=state | head -1 "
            + "| awk -F\" \" '{print $1}'"
        )

    def get_job_state_flags(self, study) -> [bool, bool, bool]:
        """Checks the job state of a submitted study and converts it to flags

        Args:
            study: The study data transfer object

        Returns:
            started, finished, with_error: The booleans representing the advancement of the slurm_job
        """
        job_state = self._check_job_state(study.job_id)
        return self.get_advancement_flags_from_state(job_state)

    def upload_file(self, src):
        """Uploads a file to the remote server

        Args:
            src: Path of the file to upload

        Returns:
            True if the file has been successfully sent, False otherwise
        """
        dst = f"{self.remote_base_path}/{Path(src).name}"
        return self.connection.upload_file(src, dst)

    def _list_remote_logs(self, job_id: int):
        """Lists the logs related to the job

        Returns:
            List containing the files name, empty if none is present
        """

        logs_path_signature = self.slurm_script_features.get_logs_path_signature(
            self.remote_base_path, job_id
        )
        command = f"ls  " + logs_path_signature
        output, error = self.connection.execute_command(command)

        def path_leaf(path):
            head, tail = ntpath.split(path)
            return tail or ntpath.basename(head)

        list_of_files = []
        if output and not error:
            list_of_files = [path_leaf(Path(file)) for file in output.splitlines()]

        return list_of_files

    def download_logs(self, study: StudyDTO):
        """Download the slurm logs of a given study

        Args:
            study: The study data transfer object

        Returns:
            True if all the logs have been downloaded, False if all the logs have not been downloaded or if there are
            no files to download
        """
        file_list = self._list_remote_logs(study.job_id)
        if file_list:
            return_flag = True
            for file in file_list:
                src = self.remote_base_path + "/" + file
                dst = str(Path(study.job_log_dir) / file)
                return_flag = return_flag and self.connection.download_file(src, dst)
        else:
            return_flag = False
        return return_flag

    def check_final_zip_not_empty(self, study: StudyDTO, final_zip_name: str):
        """Checks if finished-job.zip is not empty

        Args:
            study:
            final_zip_name:

        Returns:
            True if the final zip exists, False otherwise
        """
        return_flag = False
        if study.finished:
            filename = self.remote_base_path + "/" + final_zip_name
            if self.connection.check_file_not_empty(filename) is True:
                return_flag = True
        return return_flag

    def download_final_zip(self, study: StudyDTO):
        """Downloads the final zip containing the output fo Antares

        Args:
            study: The study that will be downloaded

        Returns:
            True if the zip has been successfully downloaded, false otherwise
        """
        final_zip_name = self.slurm_script_features.get_final_zip_name(
            study.name, study.job_id, study.run_mode
        )

        if self.check_final_zip_not_empty(study, final_zip_name):
            if study.local_final_zipfile_path:
                local_final_zipfile_path = study.local_final_zipfile_path
            else:
                local_final_zipfile_path = str(Path(study.output_dir) / final_zip_name)
                src = self.remote_base_path + "/" + final_zip_name
                dst = str(local_final_zipfile_path)
                if not self.connection.download_file(src, dst):
                    local_final_zipfile_path = None
        else:
            local_final_zipfile_path = None
        return local_final_zipfile_path

    def remove_input_zipfile(self, study: StudyDTO):
        """Removes initial zipfile

        Args:
            study: The study that will be downloaded

        Returns:
            True if the file has been successfully removed, False otherwise
        """
        if not study.input_zipfile_removed:
            zip_name = Path(study.zipfile_path).name
            study.input_zipfile_removed = self.connection.remove_file(
                f"{self.remote_base_path}/{zip_name}"
            )
        return study.input_zipfile_removed

    def remove_remote_final_zipfile(self, study: StudyDTO):
        """Removes final zipfile

        Args:
            study: The study that will be downloaded

        Returns:
            True if the file has been successfully removed, False otherwise
        """
        return self.connection.remove_file(
            f"{self.remote_base_path}/{Path(study.local_final_zipfile_path).name}"
        )

    def clean_remote_server(self, study: StudyDTO):
        """
        Removes the input and the output zipfile from the remote host

        Args:
            study: The study that will be downloaded

        Returns:
            True if all files have been removed, False otherwise
        """
        return_flag = False
        if not study.remote_server_is_clean:
            return_flag = self.remove_remote_final_zipfile(
                study
            ) & self.remove_input_zipfile(study)
        return return_flag
