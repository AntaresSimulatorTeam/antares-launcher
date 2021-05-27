import logging
from typing import List

import tinydb
from tinydb import TinyDB, where

from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.study_dto import StudyDTO


class DataRepoTinydb(IDataRepo):
    def __init__(self, database_file_path, db_primary_key: str):
        super(DataRepoTinydb, self).__init__()
        self.database_file_path = database_file_path
        self.logger = logging.getLogger(__name__ + "." + __class__.__name__)
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
        key = self.db_primary_key
        value = study.__getattribute__(key)
        self.logger.info(f"Checking if study {study.path}: is inside database")

        found_studies = self.db.search(where(key=key) == value)
        return len(found_studies) == 1

    def is_job_id_inside_database(self, job_id: int):
        """Checks if a study inside the database has the requested job_id

        Args:
            job_id: int

        Returns:
            True a study inside the database has the correct job_id, False otherwise
        """
        studies_list = self.get_list_of_studies()
        output = False
        for study in studies_list:
            if study.job_id == job_id:
                output = True
        return output

    def get_list_of_studies(self) -> List[StudyDTO]:
        """
        Returns:
            List of all studies inside the database
        """
        self.logger.info("Retrieving list of studies from the database")
        study_list = []
        for doc in self.db.all():
            study_list.append(self.doc_to_study(doc))
        return study_list

    def save_study(self, study: StudyDTO):
        """Saves the selected study inside the database. If the study already exists inside the
        database then the content of the database is updated, otherwise the new study is added to the database

        Args:
            study: The study data transfer object that will be saved
        """
        if self.is_study_inside_database(study=study):
            self.logger.info(
                f"Updating study already existing inside database with"
                f"{self.db_primary_key}: {study.__getattribute__(self.db_primary_key)}"
            )
            self.db.update(
                study.__dict__,
                where(self.db_primary_key)
                == study.__getattribute__(self.db_primary_key),
            )
        else:
            self.logger.info(
                f"Inserting new study with {self.db_primary_key}: {study.__getattribute__(self.db_primary_key)} inside database"
            )
            self.db.insert(study.__dict__)

    def remove_study(self, study_name: str) -> None:
        self.logger.info(f"Removing study with {self.db_primary_key}:{study_name}")
        self.db.remove(where(self.db_primary_key) == study_name)
