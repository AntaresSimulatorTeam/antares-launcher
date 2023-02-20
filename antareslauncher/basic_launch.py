from pathlib import Path

from antareslauncher.config import Config, get_config_path
from antareslauncher.main import MainParameters, run_with
from antareslauncher.main_option_parser import MainOptionParser, ParserParameters
from antareslauncher.parameters_reader import ParametersReader


def main():
    config_path: Path = get_config_path()
    config = Config.load_config(config_path)
    param_reader = ParametersReader(
        json_ssh_conf=config.ssh_config.config_path,
        yaml_filepath=config.config_path,
    )
    parser_parameters: ParserParameters = param_reader.get_parser_parameters()
    parser: MainOptionParser = MainOptionParser(parser_parameters)
    parser.add_basic_arguments()
    arguments = parser.parse_args()
    main_parameters: MainParameters = param_reader.get_main_parameters()
    run_with(arguments=arguments, parameters=main_parameters, show_banner=True)


if __name__ == "__main__":
    main()
