import pytest

from antareslauncher.parameters_reader import ParametersReader


def test_ParametersReader_raises_exception_with_no_file(tmp_path):
    empty_yaml = tmp_path / 'empty.yaml'
    with pytest.raises(FileNotFoundError):
        ParametersReader(empty_yaml)


def test_get_option_parameters_raises_exception_with_empty_file(tmp_path):
    empty_yaml = tmp_path / 'empty.yaml'
    empty_yaml.write_text("")
    with pytest.raises(ParametersReader.EmptyFileException):
        ParametersReader(empty_yaml).get_option_parameters()


def test_get_option_parameters_raises_exception_if_params_are_missing(tmp_path):
    empty_yaml = tmp_path / 'empty.yaml'
    empty_yaml.write_text('LOG_DIR : "LOGS"\n'
                          'STUDIES_IN_DIR : "STUDIES-IN"\n'
                          'FINISHED_DIR : "FINISHED"\n'
                          'DEFAULT_TIME_LIMIT : 172800\n'
                          'DEFAULT_N_CPU : 2\n')
    with pytest.raises(ParametersReader.MissingValueException):
        ParametersReader(empty_yaml).get_option_parameters()

