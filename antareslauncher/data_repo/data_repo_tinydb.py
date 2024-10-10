import copy
import logging
import typing as t

import tinydb

from antareslauncher.study_dto import StudyDTO

logger = logging.getLogger(__name__)


def _calc_diff(
    old: t.Mapping[str, t.Any],
    new: t.Mapping[str, t.Any],
) -> t.Mapping[str, t.Any]:
    old_keys = frozenset(old)
    new_keys = frozenset(new)
    diff_map = {
        "DEL": {k: old[k] for k in old_keys - new_keys},
        "ADD": {k: new[k] for k in new_keys - old_keys},
        "UPD": {
            k: f"{old[k]!r} => {new[k]!r}"
            for k in old_keys & new_keys
            if old[k] != new[k]
        },
    }
    diff_map = {k: v for k, v in diff_map.items() if v}
    return diff_map


class DataRepoTinydb:
    def __init__(self, database_file_path, db_primary_key: str):
        super(DataRepoTinydb, self).__init__()
        self.database_file_path = database_file_path
        self.db_primary_key = db_primary_key

    @property
    def db(self) -> tinydb.database.TinyDB:
        if not hasattr(self, "_tiny_db"):
            db = tinydb.TinyDB(self.database_file_path, sort_keys=True, indent=4)
            setattr(self, "_tiny_db", db)
        return getattr(self, "_tiny_db")

    def is_study_inside_database(self, study: StudyDTO) -> bool:
        """Get the study with selected primary key from the database

        Args:
            study: the study that will be looked for in the DB

        Returns:
            True if the study has been found and is unique inside the database, False otherwise
        """
        pk_name = self.db_primary_key
        pk_value = getattr(study, pk_name)
        found_studies = self.db.search(tinydb.where(key=pk_name) == pk_value)
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

    def get_list_of_studies(self) -> t.Sequence[StudyDTO]:
        """
        Returns:
            List of all studies inside the database
        """
        return [StudyDTO.from_dict(doc) for doc in self.db.all()]

    def save_study(self, study: StudyDTO):
        """Saves the selected study inside the database. If the study already exists inside the
        database then the content of the database is updated, otherwise the new study is added to the database

        Args:
            study: The study data transfer object that will be saved
        """
        pk_name = self.db_primary_key
        pk_value = getattr(study, pk_name)
        old = self.db.get(tinydb.where(pk_name) == pk_value)
        study_dict = vars(study)
        new = copy.deepcopy(study_dict)  # to avoid modifying the study object
        new["antares_version"] = f"{new['antares_version']:2d}"
        if old:
            diff = _calc_diff(old, new)
            logger.info(f"Updating study '{pk_value}' in database: {diff!r}")
            self.db.update(new, tinydb.where(pk_name) == pk_value)
        else:
            logger.info(f"Inserting study '{pk_value}' in database: {new!r}")
            self.db.insert(new)

    def remove_study(self, study_name: str) -> None:
        pk_name = self.db_primary_key
        logger.info(f"Removing study '{study_name}' from database")
        self.db.remove(tinydb.where(pk_name) == study_name)
