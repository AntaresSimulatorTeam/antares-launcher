import sys
from pathlib import Path

from antareslauncher.config import Config, get_config_path
from antareslauncher.main import MainParameters, run_with
from antareslauncher.main_option_parser import MainOptionParser, ParserParameters
from antareslauncher.parameters_reader import ParametersReader


def main() -> None:
    config_path: Path = get_config_path()
    config = Config.load_config(config_path)
    param_reader = ParametersReader(
        json_ssh_conf=config.ssh_config.config_path,
        yaml_filepath=config.config_path,
    )
    parser_parameters: ParserParameters = param_reader.get_parser_parameters()
    parser: MainOptionParser = MainOptionParser(parser_parameters)
    parser.add_basic_arguments(antares_versions=param_reader.antares_versions)
    ssh_config_required = parser_parameters.ssh_config_file_is_required
    alt_ssh_paths = [
        parser_parameters.ssh_configfile_path_alternate1,
        parser_parameters.ssh_configfile_path_alternate1,
    ]
    parser.add_advanced_arguments(
        ssh_config_required=ssh_config_required,
        alt_ssh_paths=alt_ssh_paths,
    )
    arguments = parser.parser.parse_args(sys.argv[1:])
    main_parameters: MainParameters = param_reader.get_main_parameters()
    run_with(arguments=arguments, parameters=main_parameters, show_banner=True)


if __name__ == "__main__":
    main()
