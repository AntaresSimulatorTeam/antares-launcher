from unittest.mock import Mock

from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.study_dto import StudyDTO


def test_data_reporter_calls_repo_to_save_study():
    # given
    data_repo = Mock(spec_set=IDataRepo)
    data_repo.save_study = Mock()
    data_reporter = DataReporter(data_repo)
    study = StudyDTO(path="empty_path")
    # when
    data_reporter.save_study(study)
    # then
    data_repo.save_study.assert_called_once_with(study)
