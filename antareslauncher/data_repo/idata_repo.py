from abc import ABC, abstractmethod
from typing import List

from antareslauncher.study_dto import StudyDTO


class IDataRepo(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_list_of_studies(self) -> List[StudyDTO]:
        raise NotImplementedError

    @abstractmethod
    def save_study(self, study: StudyDTO):
        raise NotImplementedError

    @abstractmethod
    def is_study_inside_database(self, study: StudyDTO) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_job_id_inside_database(self, job_id: int):
        raise NotImplementedError
