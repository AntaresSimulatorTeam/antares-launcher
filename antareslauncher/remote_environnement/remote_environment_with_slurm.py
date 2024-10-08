import enum
import getpass
import logging
import re
import shlex
import socket
import textwrap
import time
import typing as t
from pathlib import Path, PurePosixPath

from antareslauncher.remote_environnement.slurm_script_features import ScriptParametersDTO, SlurmScriptFeatures
from antareslauncher.remote_environnement.ssh_connection import SshConnection
from antareslauncher.study_dto import StudyDTO
from antares.study.version import SolverMinorVersion

logger = logging.getLogger(__name__)


class RemoteEnvBaseError(Exception):
    """Base class of the `RemoteEnvironmentWithSlurm` exceptions"""


class GetJobStateError(RemoteEnvBaseError):
    def __init__(self, job_id: int, job_name: str, reason: str):
        msg = f"Unable to retrieve the status of the SLURM job {job_id} (study job '{job_name}). {reason}"
        super().__init__(msg)


class JobNotFoundError(RemoteEnvBaseError):
    def __init__(self, job_id: int, job_name: str):
        msg = f"Unable to retrieve the status of the SLURM job {job_id} (study job '{job_name}): Job not found."
        super().__init__(msg)


class NoRemoteBaseDirError(RemoteEnvBaseError):
    def __init__(self, remote_base_path: PurePosixPath):
        msg = f"Unable to create the remote base directory: '{remote_base_path}"
        super().__init__(msg)


class NoLaunchScriptFoundError(RemoteEnvBaseError):
    def __init__(self, remote_path: str):
        msg = f"Launch script not found in remote server: '{remote_path}."
        super().__init__(msg)


class KillJobError(RemoteEnvBaseError):
    def __init__(self, job_id: int, reason: str):
        msg = f"Unable to kill the SLURM job {job_id}: {reason}"
        super().__init__(msg)


class SubmitJobError(RemoteEnvBaseError):
    def __init__(self, study_name: str, reason: str):
        msg = f"Unable to sumit the Antares Job {study_name} to the SLURM: {reason}"
        super().__init__(msg)


class JobStateCodes(enum.Enum):
    # noinspection SpellCheckingInspection
    """
    The `sacct` command returns the status of each task in a column named State or JobState.
    The possible values for this column depend on the cluster management system
    you are using, but here are some of the most common values:
    """
    # Job terminated due to launch failure, typically due to a hardware failure
    # (e.g. unable to boot the node or block and the job can not be requeued).
    BOOT_FAIL = "BOOT_FAIL"

    # Job was explicitly cancelled by the user or system administrator.
    # The job may or may not have been initiated.
    CANCELLED = "CANCELLED"

    # Job has terminated all processes on all nodes with an exit code of zero.
    COMPLETED = "COMPLETED"

    # Indicates that the only job on the node or that all jobs on the node are in the process of completing.
    COMPLETING = "COMPLETING"

    # Job terminated on deadline.
    DEADLINE = "DEADLINE"

    # Job terminated with non-zero exit code or other failure condition.
    FAILED = "FAILED"

    # Job terminated due to failure of one or more allocated nodes.
    NODE_FAIL = "NODE_FAIL"

    # Job experienced out of memory error.
    OUT_OF_MEMORY = "OUT_OF_MEMORY"

    # Job is awaiting resource allocation.
    PENDING = "PENDING"

    # Job terminated due to preemption.
    PREEMPTED = "PREEMPTED"

    # Job currently has an allocation.
    RUNNING = "RUNNING"

    # Job was requeued.
    REQUEUED = "REQUEUED"

    # Job is about to change size.
    RESIZING = "RESIZING"

    # Sibling was removed from cluster due to other cluster starting the job.
    REVOKED = "REVOKED"

    # Job has an allocation, but execution has been suspended and
    # CPUs have been released for other jobs.
    SUSPENDED = "SUSPENDED"

    # Job terminated upon reaching its time limit.
    TIMEOUT = "TIMEOUT"


class RemoteEnvironmentWithSlurm:
    """Class that represents the remote environment"""

    def __init__(
        self,
        _connection: SshConnection,
        slurm_script_features: SlurmScriptFeatures,
    ):
        self.connection = _connection
        self.slurm_script_features = slurm_script_features
        self.remote_base_path: str = ""
        self._initialise_remote_path()
        self._check_remote_script()

    def _initialise_remote_path(self):
        remote_home_dir = PurePosixPath(self.connection.home_dir)
        remote_base_path = remote_home_dir.joinpath(f"REMOTE_{getpass.getuser()}_{socket.gethostname()}")
        self.remote_base_path = str(remote_base_path)
        if not self.connection.make_dir(self.remote_base_path):
            raise NoRemoteBaseDirError(remote_base_path)

    def _check_remote_script(self):
        remote_antares_script = self.slurm_script_features.solver_script_path
        if not self.connection.check_file_not_empty(remote_antares_script):
            raise NoLaunchScriptFoundError(remote_antares_script)

    def get_queue_info(self) -> str:
        """This function return the information from: squeue -u run-antares

        Returns:
            The error if connection.execute_command raises an error, otherwise the slurm queue info
        """
        username = self.connection.username
        command = f"squeue -u {username} --Format=name:40,state:12,starttime:22,TimeUsed:12,timelimit:12"
        output, error = self.connection.execute_command(command)
        return error or f"{username}@{self.connection.host}\n{output}"

    def kill_remote_job(self, job_id: int) -> None:
        """Kills job with ID

        Args:
            job_id: ID of the job to kill

        Raises:
            KillJobErrorException if the command raises an error
        """
        # noinspection SpellCheckingInspection
        command = f"scancel {job_id}"
        _, error = self.connection.execute_command(command)
        if error:
            reason = f"The command [{command}] failed: {error}"
            raise KillJobError(job_id, reason)

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
        return max(time_limit_minutes, minimum_duration_in_minutes)

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
        time_limit = self.convert_time_limit_from_seconds_to_minutes(my_study.time_limit)
        script_params = ScriptParametersDTO(
            study_dir_name=Path(my_study.path).name,
            input_zipfile_name=Path(my_study.zipfile_path).name,
            time_limit=time_limit,
            n_cpu=my_study.n_cpu,
            antares_version=SolverMinorVersion.parse(my_study.antares_version),
            run_mode=my_study.run_mode,
            post_processing=my_study.post_processing,
            other_options=my_study.other_options or "",
        )
        command = self.compose_launch_command(script_params)

        output, error = self.connection.execute_command(command)
        if error:
            reason = f"The command [{command}] failed: {error}"
            raise SubmitJobError(my_study.name, reason)

        # should match "Submitted batch job 123456"
        if match := re.match(r"Submitted.*?(?P<job_id>\d+)", output, flags=re.IGNORECASE):
            return int(match["job_id"])

        reason = f"The command [{command}] return an non-parsable output:\n{textwrap.indent(output, 'OUTPUT> ')}"
        raise SubmitJobError(my_study.name, reason)

    def get_job_state_flags(
        self,
        study,
        *,
        attempts=5,
        sleep_time=0.5,
    ) -> t.Tuple[bool, bool, bool]:
        """
        Retrieves the current state of a SLURM job with the given job ID and name.

        Args:
            study: The study to check.
            attempts: The number of attempts to make to retrieve the job state.
            sleep_time: The amount of time to wait between attempts, in seconds.

        Returns:
            started, finished, with_error: booleans representing the advancement of the SLURM job

        Raises:
            GetJobStateErrorException: If the job state cannot be retrieved after
            the specified number of attempts.
        """
        job_state = self._retrieve_slurm_control_state(study.job_id, study.name)
        if job_state is None:
            # noinspection SpellCheckingInspection
            logger.info(
                f"Job '{study.job_id}' no longer active in SLURM, the job status is read from the SACCT database..."
            )
            job_state = self._retrieve_slurm_acct_state(
                study.job_id,
                study.name,
                attempts=attempts,
                sleep_time=sleep_time,
            )
        if job_state is None:
            # noinspection SpellCheckingInspection
            logger.warning(
                f"Job '{study.job_id}' not found in SACCT database."
                f"Assuming it was recently launched and will start processing soon."
            )
            job_state = JobStateCodes.RUNNING
        return {
            # JobStateCodes ------ started, finished, with_error
            JobStateCodes.BOOT_FAIL: (False, False, False),
            JobStateCodes.CANCELLED: (True, True, True),
            JobStateCodes.COMPLETED: (True, True, False),
            JobStateCodes.COMPLETING: (True, False, False),
            JobStateCodes.DEADLINE: (True, True, True),  # similar to timeout
            JobStateCodes.FAILED: (True, True, True),
            JobStateCodes.NODE_FAIL: (True, True, True),
            JobStateCodes.OUT_OF_MEMORY: (True, True, True),
            JobStateCodes.PENDING: (False, False, False),
            JobStateCodes.PREEMPTED: (False, False, False),
            JobStateCodes.RUNNING: (True, False, False),
            JobStateCodes.REQUEUED: (False, False, False),
            JobStateCodes.RESIZING: (False, False, False),
            JobStateCodes.REVOKED: (False, False, False),
            JobStateCodes.SUSPENDED: (True, False, False),
            JobStateCodes.TIMEOUT: (True, True, True),
        }[job_state]

    def _retrieve_slurm_control_state(
        self,
        job_id: int,
        job_name: str,
    ) -> t.Optional[JobStateCodes]:
        """
        Use the `scontrol` command to retrieve job status information in SLURM.
        See: https://slurm.schedmd.com/scontrol.html
        """
        # Construct the command line arguments used to check alive jobs state.
        # noinspection SpellCheckingInspection
        args = ["scontrol", "show", "job", f"{job_id}"]
        command = " ".join(shlex.quote(arg) for arg in args)
        output, error = self.connection.execute_command(command)
        if error:
            # The command output may include an error message if the job is
            # no longer active or has been removed
            if re.search("Invalid job id specified", error):
                return None
            reason = f"The command [{command}] failed: {error}"
            raise GetJobStateError(job_id, job_name, reason)

        # We can retrieve the job state from the output of the command
        # by extracting the value of the `JobState` field.
        if match := re.search(r"JobState=(\w+)", output):
            return JobStateCodes(match[1])

        reason = f"The command [{command}] return an non-parsable output:\n{textwrap.indent(output, 'OUTPUT> ')}"
        raise GetJobStateError(job_id, job_name, reason)

    def _retrieve_slurm_acct_state(
        self,
        job_id: int,
        job_name: str,
        *,
        attempts: int = 5,
        sleep_time: float = 0.5,
    ) -> t.Optional[JobStateCodes]:
        # Construct the command line arguments used to check the jobs state.
        # See the man page: https://slurm.schedmd.com/sacct.html
        # noinspection SpellCheckingInspection
        delimiter = ","
        # noinspection SpellCheckingInspection
        args = [
            "sacct",
            f"--jobs={job_id}",
            f"--name={job_name}",
            "--format=JobID,JobName,State",
            "--parsable2",
            f"--delimiter={delimiter}",
            "--noheader",
        ]
        command = " ".join(shlex.quote(arg) for arg in args)

        # Makes several attempts to get the job state.
        # I don't really know why, but it's better to reproduce the old behavior.
        output: t.Optional[str]
        last_error: str = ""
        for attempt in range(attempts):
            output, error = self.connection.execute_command(command)
            if output is not None:
                break
            last_error = error
            time.sleep(sleep_time)
        else:
            reason = f"The command [{command}] failed after {attempts} attempts: {last_error}"
            raise GetJobStateError(job_id, job_name, reason)

        # When the output is empty it mean that the job is not found
        if not output.strip():
            return None

        # Parse the output to extract the job state.
        # The output must be a CSV-like string without header row.
        for line in output.splitlines():
            parts = line.split(delimiter)
            if len(parts) == 3:
                out_job_id, out_job_name, out_state = parts
                if out_job_id == str(job_id) and out_job_name == job_name:
                    # Match the first word only, e.g.: "CANCEL by 123456798"
                    match = re.match(r"(\w+)", out_state)
                    if not match:
                        raise GetJobStateError(job_id, job_name, f"Unable to parse the job state: '{out_state}'")
                    return JobStateCodes(match[1])

        reason = f"The command [{command}] return an non-parsable output:\n{textwrap.indent(output, 'OUTPUT> ')}"
        raise GetJobStateError(job_id, job_name, reason)

    def upload_file(self, src) -> bool:
        """Uploads a file to the remote server

        Args:
            src: Path of the file to upload

        Returns:
            True if the file has been successfully sent, False otherwise
        """
        dst = f"{self.remote_base_path}/{Path(src).name}"
        return self.connection.upload_file(src, dst)

    def download_logs(self, study: StudyDTO) -> t.Sequence[Path]:
        """
        Download the slurm logs of a given study.

        Args:
            study: The study data transfer object
            study: A data transfer object representing the study for which
            to download the log files.

        Returns:
            The paths of the downloaded logs on the local filesystem.
        """
        src_dir = PurePosixPath(self.remote_base_path)
        dst_dir = Path(study.job_log_dir)
        return self.connection.download_files(
            src_dir,
            dst_dir,
            f"*{study.job_id}*.txt",
            remove=study.finished,
        )

    def download_final_zip(self, study: StudyDTO) -> t.Optional[Path]:
        """
        Download the final ZIP file for the specified study from the remote
        server and save it to the local output directory.

        Args:
            study: A data transfer object representing the study for which
            to download the final ZIP file.

        Returns:
            The path to the downloaded ZIP file on the local filesystem,
            or `None` if the download failed or no files were downloaded.

        Note:
            This function assumes that the remote server stores the final ZIP
            file in a directory located at `self.remote_base_path`.
            The downloaded file will be saved to the local output directory
            specified in `study.output_dir`.
        """
        src_dir = PurePosixPath(self.remote_base_path)
        dst_dir = Path(study.output_dir)
        downloaded_files = self.connection.download_files(
            src_dir,
            dst_dir,
            f"finished_{study.name}_{study.job_id}.zip",
            f"finished_XPANSION_{study.name}_{study.job_id}.zip",
        )
        return next(iter(downloaded_files), None)

    def remove_input_zipfile(self, study: StudyDTO) -> bool:
        """Removes initial zipfile

        Args:
            study: The study that will be downloaded

        Returns:
            True if the file has been successfully removed, False otherwise
        """
        if not study.input_zipfile_removed:
            zip_name = Path(study.zipfile_path).name
            study.input_zipfile_removed = self.connection.remove_file(f"{self.remote_base_path}/{zip_name}")
        return study.input_zipfile_removed

    def remove_remote_final_zipfile(self, study: StudyDTO) -> bool:
        """Removes final zipfile

        Args:
            study: The study that will be downloaded

        Returns:
            True if the file has been successfully removed, False otherwise
        """
        return self.connection.remove_file(f"{self.remote_base_path}/{Path(study.local_final_zipfile_path).name}")

    def clean_remote_server(self, study: StudyDTO) -> bool:
        """
        Removes the input and the output zipfile from the remote host

        Args:
            study: The study that will be downloaded

        Returns:
            True if all files have been removed, False otherwise
        """
        return (
            False
            if study.remote_server_is_clean
            else self.remove_remote_final_zipfile(study) & self.remove_input_zipfile(study)
        )
