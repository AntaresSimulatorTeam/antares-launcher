from pathlib import Path

import yaml

from antareslauncher.main_option_parser import MainOptionsParameters


class ParametersReader:
    class EmptyFileException(TypeError):
        pass

    class MissingValueException(KeyError):
        pass

    def __init__(self, yaml_path: Path):
        with open(yaml_path) as yaml_file:
            self.yaml_content = yaml.load(yaml_file, Loader=yaml.FullLoader)

    def get_option_parameters(self):
        try:
            options = MainOptionsParameters(
                default_wait_time=self.yaml_content["DEFAULT_WAIT_TIME"],
                default_time_limit=self.yaml_content["DEFAULT_TIME_LIMIT"],
                default_n_cpu=self.yaml_content["DEFAULT_N_CPU"],
                studies_in_dir=self.yaml_content["STUDIES_IN_DIR"],
                log_dir=self.yaml_content["LOG_DIR"],
                finished_dir=self.yaml_content["FINISHED_DIR"],
                ssh_config_file_is_required=self.yaml_content["SSH_CONFIG_FILE_IS_REQUIRED"],
                ssh_configfile_path_alternate1=self.yaml_content["SSH_CONFIGFILE_PATH_ALTERNATE1"],
                ssh_configfile_path_alternate2=self.yaml_content["SSH_CONFIGFILE_PATH_ALTERNATE2"], )
        except KeyError as e:
            print(f"missing value: {str(e)}")
            raise ParametersReader.MissingValueException(e)
        except TypeError:
            raise ParametersReader.EmptyFileException
        return options