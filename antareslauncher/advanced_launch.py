import sys

from antareslauncher import definitions
from antareslauncher.main import run_with, MainParameters
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
        ssh_configfile_path_prod_cwd=definitions.SSH_CONFIGFILE_PATH_PROD_CWD,
        ssh_configfile_path_prod_user=definitions.SSH_CONFIGFILE_PATH_PROD_USER,
    )
    parser: MainOptionParser = MainOptionParser(main_options_parameters)
    parser.add_basic_arguments()
    parser.add_advanced_arguments()
    arguments = parser.parse_args()

    main_parameters = MainParameters(
        json_dir=definitions.JSON_DIR,
        default_json_db_name=definitions.DEFAULT_JSON_DB_NAME,
        slurm_script_path=definitions.SLURM_SCRIPT_PATH,
        antares_versions_on_remote_server=definitions.ANTARES_VERSIONS_ON_REMOTE_SERVER,
        default_ssh_dict_from_embedded_json=definitions.DEFAULT_SSH_DICT_FROM_EMBEDDED_JSON,
        db_primary_key=definitions.DB_PRIMARY_KEY,
    )

    run_with(arguments, main_parameters)
    if not len(sys.argv) > 1:
        input("Press ENTER to exit.")
