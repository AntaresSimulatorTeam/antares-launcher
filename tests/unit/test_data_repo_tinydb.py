from unittest import mock

import pytest
import tinydb

from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.study_dto import StudyDTO


class TestDataRepoTinydb:
    @pytest.mark.unit_test
    def test_given_data_repo_when_save_study_is_called_then_is_study_inside_database_is_called(
        self,
    ):
        # given
        repo_mock = DataRepoTinydb("", "name")
        type(repo_mock).db = mock.PropertyMock()
        repo_mock.is_study_inside_database = mock.Mock()
        study_dto = StudyDTO(path="path")
        # when
        repo_mock.save_study(study_dto)
        # then
        repo_mock.is_study_inside_database.assert_called_with(study=study_dto)

    @pytest.mark.unit_test
    def test_given_data_repo_if_study_is_inside_database_then_db_update_is_called(
        self,
    ):
        # given
        repo = DataRepoTinydb("", "name")
        repo.is_study_inside_database = mock.Mock(return_value=True)
        type(repo).db = mock.PropertyMock()
        study_dto = StudyDTO(path="path")
        # when
        repo.save_study(study_dto)
        # then
        repo.db.update.assert_called_once()

    @pytest.mark.unit_test
    def test_integration_given_data_repo_if_study_is_found_once_in_database_then_db_update_is_called(
        self,
    ):
        # given
        repo = DataRepoTinydb("", "name")
        type(repo).db = mock.PropertyMock()
        repo.db.search = mock.Mock(return_value=["A"])
        study_dto = StudyDTO(path="path")
        # when
        repo.save_study(study_dto)
        # then
        repo.db.update.assert_called_once()

    @pytest.mark.unit_test
    def test_given_data_repo_if_study_is_not_inside_database_then_db_insert_is_called(
        self,
    ):
        # given
        repo = DataRepoTinydb("", "name")
        repo.is_study_inside_database = mock.Mock(return_value=False)
        type(repo).db = mock.PropertyMock()
        study_dto = StudyDTO(path="path")
        # when
        repo.save_study(study_dto)
        # then
        repo.db.insert.assert_called_once()

    @pytest.mark.unit_test
    def test_given_db_when_get_list_of_studies_is_called_then_db_all_is_called(
        self,
    ):
        # given
        repo = DataRepoTinydb("", "name")
        repo.doc_to_study = mock.Mock(return_value=42)
        type(repo).db = mock.PropertyMock()
        repo.db.all = mock.Mock(return_value=[])
        # when
        repo.get_list_of_studies()
        # then
        repo.db.all_assert_calles_once()

    @pytest.mark.unit_test
    def test_given_db_of_n_elements_when_get_list_of_studies_is_called_then_doc_to_study_is_called_n_times(
        self,
    ):
        # given
        n = 5
        repo = DataRepoTinydb("", "name")
        repo.doc_to_study = mock.Mock(return_value=42)
        type(repo).db = mock.PropertyMock()
        repo.db.all = mock.Mock(return_value=[""] * n)
        # when
        repo.get_list_of_studies()
        # then
        assert repo.doc_to_study.call_count == n

    @pytest.mark.unit_test
    def test_given_tinydb_document_when_doc_to_study_called_then_return_corresponding_study(
        self,
    ):
        # given
        expected_study = StudyDTO(path="path")
        expected_study.job_id = 42
        expected_study.n_cpu = 999
        doc = tinydb.database.Document(expected_study.__dict__, 42)
        # when
        output_study = DataRepoTinydb.doc_to_study(doc)
        # then
        assert expected_study.__dict__ == output_study.__dict__

    @pytest.mark.unit_test
    def test_is_study_inside_database_returns_true_only_if_one_study_is_found(
        self,
    ):
        # given
        repo = DataRepoTinydb("", "name")
        type(repo).db = mock.PropertyMock()
        dummy_study = StudyDTO(path="path")
        repo.db.search = mock.Mock(return_value=["first_element"])
        # when
        output = repo.is_study_inside_database(study=dummy_study)
        # then
        assert output is True

        repo.db.search = mock.Mock(return_value=["first_element", "second_element"])
        # when
        output = repo.is_study_inside_database(study=dummy_study)
        # then
        assert output is False

        repo.db.search = mock.Mock(return_value=[])
        # when
        output = repo.is_study_inside_database(study=dummy_study)
        # then
        assert output is False

    @pytest.mark.unit_test
    def test_is_job_id_inside_database_returns_true_only_if_one_job_id_is_found(
        self,
    ):
        # given
        repo = DataRepoTinydb("", "name")
        type(repo).db = mock.PropertyMock()
        study_dto = StudyDTO(path="path")
        study_dto.job_id = 6381
        repo.get_list_of_studies = mock.Mock(return_value=[study_dto])
        repo.save_study(study_dto)
        # when
        output = repo.is_job_id_inside_database(6381)
        # then
        assert output is True
