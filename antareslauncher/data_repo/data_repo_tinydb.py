import logging
from typing import List

import tinydb
from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.study_dto import StudyDTO
from tinydb import TinyDB, where


class DataRepoTinydb(IDataRepo):
    def __init__(self, database_file_path, db_primary_key: str):
        super(DataRepoTinydb, self).__init__()
        self.database_file_path = database_file_path
        self.logger = logging.getLogger(f"{__name__}.{__class__.__name__}")
        self.db_primary_key = db_primary_key

    @property
    def db(self) -> tinydb.database.TinyDB:
        return TinyDB(self.database_file_path, sort_keys=True, indent=4)

    @staticmethod
    def doc_to_study(doc: tinydb.database.Document):
        """Create a studyDTO from a tinydb.database.Document

        Args:
            doc: Document representing a study

        Returns:
            studyDTO object
        """
        study = StudyDTO(path="empty/path")
        study.__dict__ = doc
        return study

    def is_study_inside_database(self, study: StudyDTO) -> bool:
        """Get the study with selected primary key from the database

        Args:
            study: the study that will be looked for in the DB

        Returns:
            True if the study has been found and is unique inside the database, False otherwise
        """
        pk_name = self.db_primary_key
        pk_value = getattr(study, pk_name)
        found_studies = self.db.search(where(key=pk_name) == pk_value)
        return len(found_studies) == 1

    def is_job_id_inside_database(self, job_id: int):
        """Checks if a study inside the database has the requested job_id

        Args:
            job_id: int

        Returns:
            True a study inside the database has the correct job_id, False otherwise
        """
        studies_list = self.get_list_of_studies()
        return any(study.job_id == job_id for study in studies_list)

    def get_list_of_studies(self) -> List[StudyDTO]:
        """
        Returns:
            List of all studies inside the database
        """
        return [self.doc_to_study(doc) for doc in self.db.all()]

    def save_study(self, study: StudyDTO):
        """Saves the selected study inside the database. If the study already exists inside the
        database then the content of the database is updated, otherwise the new study is added to the database

        Args:
            study: The study data transfer object that will be saved
        """
        pk_name = self.db_primary_key
        pk_value = getattr(study, pk_name)
        if self.is_study_inside_database(study=study):
            self.logger.info(f"Updating study {pk_name}='{pk_value}' in database")
            self.db.update(study.__dict__, where(pk_name) == pk_value)
        else:
            self.logger.info(f"Inserting new study {pk_name}='{pk_value}' in database")
            self.db.insert(study.__dict__)

    def remove_study(self, study_name: str) -> None:
        pk_name = self.db_primary_key
        self.logger.info(f"Removing study {pk_name}='{study_name}' from database")
        self.db.remove(where(pk_name) == study_name)
