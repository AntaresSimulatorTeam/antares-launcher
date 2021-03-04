from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.study_dto import StudyDTO


class DataReporter:
    def __init__(self, data_repo: IDataRepo):
        self._data_repo = data_repo

    def save_study(self, study: StudyDTO):
        self._data_repo.save_study(study)
