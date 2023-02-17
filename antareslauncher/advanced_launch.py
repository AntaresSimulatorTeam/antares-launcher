from pathlib import Path

from antareslauncher.main import run_with, MainParameters
from antareslauncher.main_option_parser import (
    MainOptionParser,
    ParserParameters,
)
from antareslauncher.parameters_reader import ParametersReader

HERE = Path(__file__).parent.resolve()
PACKAGE_NAME = "antareslauncher"
PROJECT_DIR = next(iter(p for p in HERE.parents if p.joinpath(PACKAGE_NAME).exists()))
DATA_DIR = PROJECT_DIR / "data"
SSH_JSON_FILE = DATA_DIR / "ssh_config.json"
YAML_CONF_FILE = DATA_DIR / "configuration.yaml"


def main():
    param_reader = ParametersReader(
        json_ssh_conf=SSH_JSON_FILE, yaml_filepath=YAML_CONF_FILE
    )
    parser_parameters: ParserParameters = param_reader.get_parser_parameters()
    parser: MainOptionParser = MainOptionParser(parser_parameters)
    parser.add_basic_arguments().add_advanced_arguments()
    arguments = parser.parse_args()
    main_parameters: MainParameters = param_reader.get_main_parameters()
    run_with(arguments=arguments, parameters=main_parameters, show_banner=True)


if __name__ == "__main__":
    main()
