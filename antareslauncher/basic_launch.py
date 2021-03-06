import sys

from antareslauncher import main, definitions
from antareslauncher.main import MainParameters
from antareslauncher.main_option_parser import (
    MainOptionParser,
    MainOptionsParameters,
)

if __name__ == "__main__":
    main_options_parameters = MainOptionsParameters(
        default_wait_time=definitions.DEFAULT_WAIT_TIME,
        default_time_limit=definitions.DEFAULT_TIME_LIMIT,
        default_n_cpu=definitions.DEFAULT_N_CPU,
        studies_in_dir=definitions.STUDIES_IN_DIR,
        log_dir=definitions.LOG_DIR,
        finished_dir=definitions.FINISHED_DIR,
        ssh_config_file_is_required=definitions.SSH_CONFIG_FILE_IS_REQUIRED,
        ssh_configfile_path_alternate1=definitions.SSH_CONFIGFILE_PATH_ALTERNATE1,
        ssh_configfile_path_alternate2=definitions.SSH_CONFIGFILE_PATH_ALTERNATE2,
    )
    parser: MainOptionParser = MainOptionParser(
        main_options_parameters=main_options_parameters
    )
    parser.add_basic_arguments()
    input_arguments = parser.parse_args()

    main_parameters = MainParameters(
        json_dir=definitions.JSON_DIR,
        default_json_db_name=definitions.DEFAULT_JSON_DB_NAME,
        slurm_script_path=definitions.SLURM_SCRIPT_PATH,
        antares_versions_on_remote_server=definitions.ANTARES_VERSIONS_ON_REMOTE_SERVER,
        default_ssh_dict_from_embedded_json=definitions.DEFAULT_SSH_DICT_FROM_EMBEDDED_JSON,
        db_primary_key=definitions.DB_PRIMARY_KEY,
    )

    main.run_with(arguments=input_arguments, parameters=main_parameters, show_banner=True)
    if not len(sys.argv) > 1:
        input("Press ENTER to exit.")
