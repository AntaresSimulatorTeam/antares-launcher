from unittest.mock import Mock

from antareslauncher.data_repo.data_provider import DataProvider
from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.study_dto import StudyDTO


def test_data_provider_return_list_of_studies_obtained_from_repo():
    # given
    data_repo = Mock(spec_set=IDataRepo)
    study = StudyDTO(path="empty_path")
    data_repo.get_list_of_studies = Mock(return_value=[study])
    data_provider = DataProvider(data_repo)
    # when
    list_of_studies = data_provider.get_list_of_studies()
    # then
    assert list_of_studies == [study]
