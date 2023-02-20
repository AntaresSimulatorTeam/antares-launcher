import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from antareslauncher import __version__
from antareslauncher.antares_launcher import AntaresLauncher
from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.logger_initializer import LoggerInitializer
from antareslauncher.remote_environnement import ssh_connection
from antareslauncher.remote_environnement.remote_environment_with_slurm import (
    RemoteEnvironmentWithSlurm,
)
from antareslauncher.remote_environnement.slurm_script_features import (
    SlurmScriptFeatures,
)
from antareslauncher.use_cases.check_remote_queue.check_queue_controller import (
    CheckQueueController,
)
from antareslauncher.use_cases.check_remote_queue.slurm_queue_show import (
    SlurmQueueShow,
)
from antareslauncher.use_cases.create_list.study_list_composer import (
    StudyListComposer,
    StudyListComposerParameters,
)
from antareslauncher.use_cases.generate_tree_structure.tree_structure_initializer import (
    TreeStructureInitializer,
)
from antareslauncher.use_cases.kill_job.job_kill_controller import (
    JobKillController,
)
from antareslauncher.use_cases.launch.launch_controller import LaunchController
from antareslauncher.use_cases.retrieve.retrieve_controller import (
    RetrieveController,
)
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater
from antareslauncher.use_cases.wait_loop_controller.wait_controller import (
    WaitController,
)


class NoJsonConfigFileError(Exception):
    pass


class SshConnectionNotEstablishedException(Exception):
    pass


# fmt: off
ANTARES_LAUNCHER_BANNER = (
    "\n"
    r"=======================================================================================" "\n"
    r"|    ___        _                       _                            _                |" "\n"
    r"|   / _ \      | |                     | |                          | |               |" "\n"
    r"|  / /_\ \_ __ | |_ __ _ _ __ ___  ___ | |     __ _ _   _ _ __   ___| |__   ___ _ __  |" "\n"
    r"|  |  _  | '_ \| __/ _` | '__/ _ \/ __|| |    / _` | | | | '_ \ / __| '_ \ / _ \ '__| |" "\n"
    r"|  | | | | | | | || (_| | | |  __/\__ \| |___| (_| | |_| | | | | (__| | | |  __/ |    |" "\n"
    r"|  \_| |_/_| |_|\__\__,_|_|  \___||___/\_____/\__,_|\__,_|_| |_|\___|_| |_|\___|_|    |" "\n"
    r"=======================================================================================" "\n"
)
# fmt: on


@dataclass
class MainParameters:
    json_dir: Path
    default_json_db_name: str
    slurm_script_path: str
    antares_versions_on_remote_server: List[str]
    default_ssh_dict: Dict
    db_primary_key: str


def run_with(
    arguments: argparse.Namespace, parameters: MainParameters, show_banner=False
):
    """Instantiates all the objects necessary to antares-launcher, and runs the program"""
    if arguments.version:
        print(f"Antares_Launcher v{__version__}")
        return

    if show_banner:
        print(ANTARES_LAUNCHER_BANNER)

    display = DisplayTerminal()
    file_manager = FileManager(display)

    db_json_file_path = parameters.json_dir / parameters.default_json_db_name

    tree_structure_initializer = TreeStructureInitializer(
        display,
        file_manager,
        arguments.studies_in,
        arguments.log_dir,
        arguments.output_dir,
    )

    tree_structure_initializer.init_tree_structure()
    logger_initializer = LoggerInitializer(
        str(Path(arguments.log_dir) / "antares_launcher.log")
    )
    logger_initializer.init_logger()

    # connection
    ssh_dict = get_ssh_config_dict(
        file_manager,
        arguments.json_ssh_config,
        parameters.default_ssh_dict,
    )
    connection = ssh_connection.SshConnection(config=ssh_dict)
    verify_connection(connection, display)

    slurm_script_features = SlurmScriptFeatures(parameters.slurm_script_path)
    environment = RemoteEnvironmentWithSlurm(connection, slurm_script_features)
    data_repo = DataRepoTinydb(
        database_file_path=db_json_file_path, db_primary_key=parameters.db_primary_key
    )
    study_list_composer = StudyListComposer(
        repo=data_repo,
        file_manager=file_manager,
        display=display,
        parameters=StudyListComposerParameters(
            studies_in_dir=arguments.studies_in,
            time_limit=arguments.time_limit,
            log_dir=arguments.log_dir,
            n_cpu=arguments.n_cpu,
            xpansion_mode=arguments.xpansion_mode,
            output_dir=arguments.output_dir,
            post_processing=arguments.post_processing,
            antares_versions_on_remote_server=parameters.antares_versions_on_remote_server,
            other_options=arguments.other_options or "",
        ),
    )
    launch_controller = LaunchController(
        repo=data_repo,
        env=environment,
        file_manager=file_manager,
        display=display,
    )
    state_updater = StateUpdater(env=environment, display=display)
    retrieve_controller = RetrieveController(
        repo=data_repo,
        env=environment,
        file_manager=file_manager,
        display=display,
        state_updater=state_updater,
    )
    slurm_queue_show = SlurmQueueShow(env=environment, display=display)
    check_queue_controller = CheckQueueController(
        slurm_queue_show=slurm_queue_show,
        state_updater=state_updater,
        repo=data_repo,
    )
    job_kill_controller = JobKillController(
        env=environment,
        display=display,
        repo=data_repo,
    )
    wait_controller = WaitController(display=display)

    launcher = AntaresLauncher(
        study_list_composer=study_list_composer,
        launch_controller=launch_controller,
        retrieve_controller=retrieve_controller,
        job_kill_controller=job_kill_controller,
        check_queue_controller=check_queue_controller,
        wait_controller=wait_controller,
        wait_mode=arguments.wait_mode,
        wait_time=arguments.wait_time,
        job_id_to_kill=arguments.job_id_to_kill,
        xpansion_mode=arguments.xpansion_mode,
        check_queue_bool=arguments.check_queue,
    )
    launcher.run()


def verify_connection(connection, display):
    if connection.test_connection():
        display.show_message(f"SSH connection to {connection.host} established", __name__)
    else:
        raise Exception(f"Could not establish SSH connection to {connection.host}")


def get_ssh_config_dict(file_manager, json_ssh_config, ssh_dict: dict):
    if json_ssh_config is None:
        ssh_dict = ssh_dict
    else:
        ssh_dict = file_manager.convert_json_file_to_dict(json_ssh_config)
    if ssh_dict is None:
        raise Exception("Could not find any SSH configuration file")
    return ssh_dict
