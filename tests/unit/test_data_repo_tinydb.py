import random
from pathlib import Path

import pytest

from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.study_dto import StudyDTO


@pytest.fixture(name="repo")
def repo_fixture(tmp_path: Path) -> DataRepoTinydb:
    return DataRepoTinydb(
        database_file_path=tmp_path.joinpath("repo.json"),
        db_primary_key="name",
    )


class TestDataRepoTinydb:
    @pytest.mark.unit_test
    def test_save_study__insert_and_update(self, repo: DataRepoTinydb):
        """
        Test that the 'save_study' method in DataRepoTinydb correctly adds a study to the database
        and that 'is_study_inside_database' is called with the same study object.
        """
        study = StudyDTO(path="path/to/my_study")
        repo.save_study(study)
        assert repo.is_study_inside_database(study)
        studies = repo.get_list_of_studies()
        assert {s.name for s in studies} == {"my_study"}

        study.started = True
        repo.save_study(study)
        assert repo.is_study_inside_database(study)
        studies = repo.get_list_of_studies()
        assert {s.name for s in studies} == {"my_study"}
        actual_study = next(iter(studies))
        assert actual_study.started is True

    @pytest.mark.unit_test
    def test_remove_study__nominal_case(self, repo: DataRepoTinydb):
        study = StudyDTO(path="path/to/my_study")
        repo.save_study(study)
        repo.remove_study("my_study")
        studies = repo.get_list_of_studies()
        assert not studies

    @pytest.mark.unit_test
    def test_remove_study__missing(self, repo: DataRepoTinydb):
        repo.remove_study("missing_study")
        studies = repo.get_list_of_studies()
        assert not studies

    @pytest.mark.unit_test
    def test_is_job_id_inside_database(self, repo: DataRepoTinydb):
        job_id = random.randint(1, 1000)
        study = StudyDTO(path="path/to/my_study", job_id=job_id)
        repo.save_study(study)
        assert repo.is_job_id_inside_database(job_id)
        assert not repo.is_job_id_inside_database(9999)
