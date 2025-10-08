import dataclasses
import shlex

from antareslauncher.study_dto import Modes
from antares.study.version import SolverMinorVersion


@dataclasses.dataclass
class ScriptParametersDTO:
    study_dir_name: str
    input_zipfile_name: str
    time_limit: int
    n_cpu: int
    antares_version: SolverMinorVersion
    run_mode: Modes
    post_processing: bool
    other_options: str


class SlurmScriptFeatures:
    """Class that returns data related to the remote SLURM script
    Installed on the remote server"""

    def __init__(
        self,
        slurm_script_path: str,
        *,
        partition: str,
        quality_of_service: str,
    ):
        """
        Initialize the slurm script feature.

        Args:
            slurm_script_path: Path to the SLURM script used to launch studies (a Shell script).
            partition: Request a specific partition for the resource allocation.
                If not specified, the default behavior is to allow the slurm controller
                to select the default partition as designated by the system administrator.
            quality_of_service: Request a quality of service for the job.
                QOS values can be defined for each user/cluster/account association in the Slurm database.
        """
        self.solver_script_path = slurm_script_path
        self.partition = partition
        self.quality_of_service = quality_of_service

    def compose_launch_command(
        self,
        remote_launch_dir: str,
        script_params: ScriptParametersDTO,
    ) -> str:
        """
        Compose and return the complete command to be executed to launch the Antares Solver script.

        Args:
            remote_launch_dir: remote directory where the script is launched
            script_params: ScriptFeaturesDTO dataclass container for script parameters

        Returns:
            str: the complete command to be executed to launch a study on the SLURM server
        """
        # The following options can be added to the `sbatch` command
        # if they are not empty (or null for integer options).
        _opts = {
            "--partition": self.partition,  # non-empty string
            "--qos": self.quality_of_service,  # non-empty string
            "--job-name": script_params.study_dir_name,  # non-empty string
            "--time": script_params.time_limit,  # greater than 0
            "--cpus-per-task": script_params.n_cpu,  # greater than 0
        }

        _job_type = {
            Modes.antares: "ANTARES",  # Mode for Antares Solver
            Modes.xpansion_r: "ANTARES_XPANSION_R",  # Mode for Old Xpansion implemented in R
            Modes.xpansion_cpp: "ANTARES_XPANSION_CPP",  # Mode for Xpansion implemented in C++
        }[script_params.run_mode]

        # Construct the `sbatch` command
        args = ["sbatch"]
        args.extend(f"{k}={shlex.quote(str(v))}" for k, v in _opts.items() if v)
        args.extend(
            shlex.quote(arg)
            for arg in [
                self.solver_script_path,
                script_params.input_zipfile_name,
                f"{script_params.antares_version:2d}",
                _job_type,
                str(script_params.post_processing),
            ]
        )
        launch_cmd = f"cd {remote_launch_dir} && {' '.join(args)} '{script_params.other_options}'"
        return launch_cmd
