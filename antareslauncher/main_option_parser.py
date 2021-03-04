import argparse
import getpass
import pathlib
from argparse import RawTextHelpFormatter
from typing import List

from antareslauncher import definitions


class MainOptionParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
        self.default_argument_values = {}
        self._set_default_argument_values()

    def _set_default_argument_values(self) -> None:
        """Fills the "default_argument_values" dictionary"""
        self.default_argument_values = {
            "wait_mode": False,
            "wait_time": definitions.DEFAULT_WAIT_TIME,
            "studies_in": str(definitions.STUDIES_IN_DIR),
            "output_dir": str(definitions.FINISHED_DIR),
            "check_queue": False,
            "time_limit": definitions.DEFAULT_TIME_LIMIT,
            "json_ssh_config": look_for_default_ssh_conf_file(),
            "log_dir": str(definitions.LOG_DIR),
            "n_cpu": definitions.DEFAULT_N_CPU,
            "job_id_to_kill": None,
            "xpansion_mode": False,
            "version": False,
            "post_processing": False,
        }

    def parse_args(self, args: List[str] = None) -> argparse.Namespace:
        """Parses the args given with the selected options.
        If args is None, the standard input will be parsed

        Args:
            args: Arguments given to the program

        Returns:
            argparse.Namespace: namespace containing all the options

        """
        output: argparse.Namespace = self.parser.parse_args(args)

        for key, value in self.default_argument_values.items():
            if not hasattr(output, key):
                setattr(output, key, value)
        return output

    def add_basic_arguments(self) -> None:
        """Adds to the parser all the arguments for the light mode"""
        self.parser.add_argument(
            "-w",
            "--wait-mode",
            action="store_true",
            dest="wait_mode",
            default=self.default_argument_values["wait_mode"],
            help="Activate the wait mode: the Antares_Launcher waits for all the jobs to finish\n"
            "it check every WAIT_TIME seconds (default value = 900 = 15 minutes).",
        )

        self.parser.add_argument(
            "--wait-time",
            dest="wait_time",
            type=int,
            default=self.default_argument_values["wait_time"],
            help="Number of seconds between each verification of the end of the simulations\n"
            "changes the value of WAIT_TIME used for the wait-mode.",
        )

        self.parser.add_argument(
            "-i",
            "--studies-in-dir",
            dest="studies_in",
            default=self.default_argument_values["studies_in"],
            help="Directory containing the studies to be executed.\n"
            "If the directory does not exist, it will be created (empty).\n"
            "if no directory is indicated, the default value will be used STUDIES-IN",
        )

        self.parser.add_argument(
            "-o",
            "--output-dir",
            dest="output_dir",
            default=self.default_argument_values["output_dir"],
            help="Directory where the finished studies will be downloaded and extracted.\n"
            'If the directory does not exist, it will be created (default value "FINISHED").',
        )

        self.parser.add_argument(
            "-q",
            "--check-queue",
            action="store_true",
            dest="check_queue",
            default=self.default_argument_values["check_queue"],
            help="Displays from the remote queue all job statuses.\n"
            "If the option is used, it will override the standard execution.\n"
            "It can be overridden by the kill job option (-k).",
        )

        self.parser.add_argument(
            "-t",
            "--time-limit",
            dest="time_limit",
            type=int,
            default=self.default_argument_values["time_limit"],
            help="Time limit in seconds of a single job.\n"
            "If nothing is specified here and"
            "if the study is not initialised with a specific value,\n"
            f"the default value will be used: {definitions.DEFAULT_TIME_LIMIT}={int(definitions.DEFAULT_TIME_LIMIT/3600)}h.",
        )

        self.parser.add_argument(
            "-x",
            "--xpansion-mode",
            action="store_true",
            dest="xpansion_mode",
            default=False,
            help="Activate the xpansion mode:\n"
            "Antares_Launcher will launch all the new studies in xpansion mode if\n"
            "the studies contains the information necessary for AntaresXpansion",
        )

        self.parser.add_argument(
            "-v",
            "--version",
            action="store_true",
            dest="version",
            default=False,
            help="Shows the version of Antares_Launcher",
        )

        self.parser.add_argument(
            "-p",
            "--post-processing",
            action="store_true",
            dest="post_processing",
            default=False,
            help='Enables the post processing of the antares study by executing the "post_processing.R" file',
        )

        self.parser.add_argument(
            "-k",
            "--kill-job",
            dest="job_id_to_kill",
            type=int,
            default=self.default_argument_values["job_id_to_kill"],
            help=f"JobID of the run to be cancelled on the remote server.\n"
            f"the JobID can be retrieved with option -q to show the queue."
            f"If option is given it overrides the -q and the standard execution.",
        )

    def add_advanced_arguments(self) -> None:
        """Adds to the parser all the arguments for the advanced mode"""
        self.parser.add_argument(
            "-n",
            "--n-cores",
            dest="n_cpu",
            type=int,
            default=self.default_argument_values["n_cpu"],
            help=f"Number of cores to be used for a single job.\n"
            f"If nothing is specified here and "
            f"if the study is not initialised with a specific value,\n"
            f"the default value will be used: n_cpu=={definitions.DEFAULT_N_CPU}",
        )

        self.parser.add_argument(
            "--log-dir",
            dest="log_dir",
            default=self.default_argument_values["log_dir"],
            help="Directory where the logs of the jobs will be found.\n"
            "If the directory does not exist, it will be created.",
        )

        self.parser.add_argument(
            "--ssh-settings-file",
            dest="json_ssh_config",
            default=self.default_argument_values["json_ssh_config"],
            required=definitions.SSH_CONFIG_FILE_IS_REQUIRED,
            help=f"Path to the configuration file for the ssh connection.\n"
            f"If no value is given, "
            f"it will look for it in default location with this order:\n"
            f"1st: {definitions.SSH_CONFIGFILE_PATH_PROD_CWD}\n"
            f"2nd: {definitions.SSH_CONFIGFILE_PATH_PROD_USER}\n"
            f"3rd: default configuration for Windows.\n",
        )


def look_for_default_ssh_conf_file() -> pathlib.Path:
    """Checks if the ssh config file exists.

    Returns:
        path to the ssh config file is it exists, None otherwise
    """
    ssh_conf_file: pathlib.Path
    if definitions.SSH_CONFIGFILE_PATH_PROD_CWD.is_file():
        ssh_conf_file = definitions.SSH_CONFIGFILE_PATH_PROD_CWD
    elif definitions.SSH_CONFIGFILE_PATH_PROD_USER.is_file():
        ssh_conf_file = definitions.SSH_CONFIGFILE_PATH_PROD_USER
    else:
        ssh_conf_file = None
    return ssh_conf_file


def get_default_db_name() -> str:
    """Uses the username to generate the db name

    Returns:
        str: The default database name
    """
    user: str = getpass.getuser()
    return f"{user}_antares_launcher_db.json"
