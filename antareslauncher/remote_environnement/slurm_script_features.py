from dataclasses import dataclass

from antareslauncher.study_dto import Modes


@dataclass
class ScriptParametersDTO:
    study_dir_name: str
    input_zipfile_name: str
    time_limit: int
    n_cpu: int
    antares_version: int
    run_mode: Modes
    post_processing: bool


class SlurmScriptFeatures:
    """Class that returns data related to the remote SLURM script
    Installed on the remote server"""

    def __init__(self, slurm_script_path: str):
        self.JOB_TYPE_PLACEHOLDER = "TO_BE_REPLACED_WITH_JOB_TYPE"
        self.JOB_TYPE_ANTARES = "ANTARES"
        self.JOB_TYPE_XPANSION = "ANTARES_XPANSION"
        self.solver_script_path = slurm_script_path
        self._script_params = None
        self._remote_launch_dir = None

    def compose_launch_command(
        self,
        remote_launch_dir: str,
        script_params: ScriptParametersDTO,
    ) -> str:
        """Compose and return the complete command to be executed to launch the Antares Solver script.
        It includes the change of directory to remote_base_path

        Args:
            script_params: ScriptFeaturesDTO dataclass container for script parameters
            remote_launch_dir: remote directory where the script is launched

        Returns:
            str: the complete command to be executed to launch the including the change of directory to remote_base_path

        """
        self._script_params = script_params
        self._remote_launch_dir = remote_launch_dir
        complete_command = self._get_complete_command_with_placeholders()

        if script_params.run_mode == Modes.antares:
            complete_command = complete_command.replace(
                self.JOB_TYPE_PLACEHOLDER, self.JOB_TYPE_ANTARES
            )
        else:
            complete_command = complete_command.replace(
                self.JOB_TYPE_PLACEHOLDER, self.JOB_TYPE_XPANSION
            )

        return complete_command

    def _bash_options(self):
        option1_zipfile_name = f' "{self._script_params.input_zipfile_name}"'
        option2_antares_version = f" {self._script_params.antares_version}"
        option3_job_type = f" {self.JOB_TYPE_PLACEHOLDER}"
        option4_post_processing = f" {self._script_params.post_processing}"
        bash_options = (
            option1_zipfile_name
            + option2_antares_version
            + option3_job_type
            + option4_post_processing
        )
        return bash_options

    def _sbatch_command_with_slurm_options(self):
        call_sbatch = f"sbatch"
        job_name = f' --job-name="{self._script_params.study_dir_name}"'
        time_limit_opt = f" --time={self._script_params.time_limit}"
        cpu_per_task = f" --cpus-per-task={self._script_params.n_cpu}"
        slurm_options = call_sbatch + job_name + time_limit_opt + cpu_per_task
        return slurm_options

    def _get_complete_command_with_placeholders(self):
        change_dir = f"cd {self._remote_launch_dir}"
        slurm_options = self._sbatch_command_with_slurm_options()
        bash_options = self._bash_options()
        submit_command = slurm_options + " " + self.solver_script_path + bash_options
        complete_command = change_dir + " && " + submit_command
        return complete_command

    @staticmethod
    def get_logs_path_signature(remote_launch_dir, job_id):
        """

        Args:
            remote_launch_dir:  remote directory where the SLURM script is launched
            job_id: slurm job id whom logs need to be listed

        Returns:
            the logfiles' signature in order to execute an ls command
            ex: remote_base_path/job*jobid*.txt

        """
        return f"{remote_launch_dir}/*{job_id}*.txt"

    @staticmethod
    def get_final_zip_name(study_name: str, job_id: int, run_mode: int):
        """Compose and return the name of the finished-job zipfile of the Antares Solver simulation

        Args:
            run_mode:
            study_name: name of the study
            job_id: SLURM job_id

        Returns:
            the name of the zip file containing the finished job

        """
        if run_mode == Modes.antares:
            final_zip_name = f"finished_{study_name}_{job_id}.zip"
        elif run_mode == Modes.xpansion:
            final_zip_name = f"finished_XPANSION_{study_name}_{job_id}.zip"
        else:
            raise ValueError

        return final_zip_name
