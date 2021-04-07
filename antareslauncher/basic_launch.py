import sys

from antareslauncher import main, definitions
from antareslauncher.main_option_parser import MainOptionParser, MainOptionsParameters

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
    parser: MainOptionParser = MainOptionParser(
        main_options_parameters=main_options_parameters
    )
    parser.add_basic_arguments()
    input_arguments = parser.parse_args()
    main.run_with(input_arguments)
    if not len(sys.argv) > 1:
        input("Press ENTER to exit.")
