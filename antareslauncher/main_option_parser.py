from __future__ import annotations

import argparse
import datetime
import getpass
import pathlib
import typing as t
from argparse import RawTextHelpFormatter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParserParameters:
    default_wait_time: int
    default_time_limit: int
    default_n_cpu: int
    studies_in_dir: str
    log_dir: str
    finished_dir: str
    ssh_config_file_is_required: bool
    ssh_configfile_path_alternate1: t.Optional[pathlib.Path]
    ssh_configfile_path_alternate2: t.Optional[pathlib.Path]


class MainOptionParser:
    def __init__(self, parameters: ParserParameters) -> None:
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
        defaults = {
            "wait_mode": False,
            "wait_time": parameters.default_wait_time,
            "studies_in": str(parameters.studies_in_dir),
            "output_dir": str(parameters.finished_dir),
            "check_queue": False,
            "time_limit": parameters.default_time_limit,
            "json_ssh_config": look_for_default_ssh_conf_file(parameters),
            "log_dir": str(parameters.log_dir),
            "n_cpu": parameters.default_n_cpu,
            "antares_version": 0,
            "job_id_to_kill": None,
            "xpansion_mode": "",
            "version": False,
            "post_processing": False,
            "other_options": None,
        }
        self.parser.set_defaults(**defaults)

    # NOTE: keep this delegation to preserve backward compatibility with v1.3.0
    def parse_args(self, args: t.Union[t.Sequence[str], None]) -> argparse.Namespace:
        return self.parser.parse_args(args)

    def add_basic_arguments(self, *, antares_versions: t.Sequence[str] = ()) -> MainOptionParser:
        """Adds to the parser all the arguments for the light mode"""
        self.parser.add_argument(
            "-w",
            "--wait-mode",
            action="store_true",
            dest="wait_mode",
            help=(
                "Activate the wait mode: the Antares_Launcher waits for all the jobs to finish\n"
                "it check every WAIT_TIME seconds (default value = 900 = 15 minutes)."
            ),
        )

        wait_time = self.parser.get_default("wait_time")
        delta = datetime.timedelta(seconds=wait_time)
        self.parser.add_argument(
            "--wait-time",
            dest="wait_time",
            type=int,
            help=(
                "Number of seconds between each verification of the end of the simulations\n"
                "changes the value of WAIT_TIME used for the wait-mode.\n"
                f"The default value will be used: {delta.total_seconds():.0f}s = {delta}."
            ),
        )

        self.parser.add_argument(
            "-i",
            "--studies-in-dir",
            dest="studies_in",
            help=(
                "Directory containing the studies to be executed.\n"
                "If the directory does not exist, it will be created (empty).\n"
                "if no directory is indicated, the default value will be used STUDIES-IN"
            ),
        )

        self.parser.add_argument(
            "-o",
            "--output-dir",
            dest="output_dir",
            help=(
                "Directory where the finished studies will be downloaded and extracted.\n"
                'If the directory does not exist, it will be created (default value "FINISHED").'
            ),
        )

        self.parser.add_argument(
            "-q",
            "--check-queue",
            action="store_true",
            dest="check_queue",
            help=(
                "Displays from the remote queue all job statuses.\n"
                "If the option is used, it will override the standard execution.\n"
                "It can be overridden by the kill job option (-k)."
            ),
        )

        time_limit = self.parser.get_default("time_limit")
        delta = datetime.timedelta(seconds=time_limit)
        self.parser.add_argument(
            "-t",
            "--time-limit",
            dest="time_limit",
            type=int,
            help=(
                "Time limit in seconds of a single job.\n"
                "If nothing is specified here and"
                "if the study is not initialised with a specific value,\n"
                f"The default value will be used: {delta.total_seconds():.0f}s = {delta}."
            ),
        )

        self.parser.add_argument(
            "-x",
            "--xpansion-mode",
            dest="xpansion_mode",
            help=(
                "Activate the xpansion mode:\n"
                "Antares_Launcher will launch all the new studies in xpansion mode if\n"
                "the studies contains the information necessary for AntaresXpansion.\n"
                'if rhe flag is set to "r", the xpansion mode will be activated with the R version.\n'
            ),
        )

        self.parser.add_argument(
            "-v",
            "--version",
            action="store_true",
            dest="version",
            help="Shows the version of Antares_Launcher",
        )

        self.parser.add_argument(
            "-p",
            "--post-processing",
            action="store_true",
            dest="post_processing",
            help='Enables the post processing of the antares study by executing the "post_processing.R" file',
        )

        self.parser.add_argument(
            "--other-options",
            dest="other_options",
            help="Other options to pass to the antares launcher script",
        )

        self.parser.add_argument(
            "-k",
            "--kill-job",
            dest="job_id_to_kill",
            type=int,
            help=(
                f"JobID of the run to be cancelled on the remote server.\n"
                f"the JobID can be retrieved with option -q to show the queue."
                f"If option is given it overrides the -q and the standard execution."
            ),
        )

        self.parser.add_argument(
            "--solver-version",
            dest="antares_version",
            type=int,
            choices=[int(v) for v in antares_versions],
            help="Antares Solver version to use for simulation",
        )

        return self

    def add_advanced_arguments(
        self,
        *,
        ssh_config_required: bool = False,
        alt_ssh_paths: t.Sequence[t.Optional[Path]] = (),
    ) -> MainOptionParser:
        """Adds to the parser all the arguments for the advanced mode"""
        n_cpu = self.parser.get_default("n_cpu")
        self.parser.add_argument(
            "-n",
            "--n-cores",
            dest="n_cpu",
            type=int,
            help=(
                f"Number of cores to be used for a single job.\n"
                f"If nothing is specified here and "
                f"if the study is not initialised with a specific value,\n"
                f"the default value will be used: n_cpu=={n_cpu}"
            ),
        )

        self.parser.add_argument(
            "--log-dir",
            dest="log_dir",
            help=(
                "Directory where the logs of the jobs will be found.\n"
                "If the directory does not exist, it will be created."
            ),
        )

        ssh_paths = "\n".join(f"'{p}'" for p in dict.fromkeys(alt_ssh_paths))
        self.parser.add_argument(
            "--ssh-settings-file",
            dest="json_ssh_config",
            required=ssh_config_required,
            help=(
                f"Path to the configuration file for the ssh connection.\n"
                f"If no value is given, "
                f"it will look for it in default location with this order:\n"
                f"{ssh_paths}"
            ),
        )
        return self


def look_for_default_ssh_conf_file(
    parameters: ParserParameters,
) -> t.Union[None, pathlib.Path]:
    """Checks if the ssh config file exists.

    Returns:
        path to the ssh config file is it exists, None otherwise
    """
    if parameters.ssh_configfile_path_alternate1 and parameters.ssh_configfile_path_alternate1.is_file():
        return parameters.ssh_configfile_path_alternate1
    elif parameters.ssh_configfile_path_alternate2 and parameters.ssh_configfile_path_alternate2.is_file():
        return parameters.ssh_configfile_path_alternate2
    else:
        return None


def get_default_db_name() -> str:
    """Uses the username to generate the db name

    Returns:
        str: The default database name
    """
    user: str = getpass.getuser()
    return f"{user}_antares_launcher_db.json"
