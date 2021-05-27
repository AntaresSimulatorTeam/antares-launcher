import sys
from pathlib import Path

from antareslauncher.main import run_with, MainParameters
from antareslauncher.main_option_parser import (
    MainOptionParser,
    ParserParameters,
)
from antareslauncher.parameters_reader import ParametersReader

DATA_DIR = Path(__file__).parent.resolve() / "data"
SSH_JSON_FILE = DATA_DIR / "sshconfig.json"
YAML_CONF_FILE = DATA_DIR / "configuration.yaml"

if __name__ == "__main__":

    param_reader = ParametersReader(
        json_ssh_conf=SSH_JSON_FILE, yaml_filepath=YAML_CONF_FILE
    )
    parser_parameters: ParserParameters = param_reader.get_parser_parameters()
    parser: MainOptionParser = MainOptionParser(parser_parameters)
    parser.add_basic_arguments()
    arguments = parser.parse_args()

    main_parameters: MainParameters = param_reader.get_main_parameters()

    run_with(arguments=arguments, parameters=main_parameters, show_banner=True)
    if not len(sys.argv) > 1:
        input("Press ENTER to exit.")
