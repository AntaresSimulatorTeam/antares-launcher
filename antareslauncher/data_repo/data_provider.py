from dataclasses import dataclass

from antareslauncher.data_repo.idata_repo import IDataRepo


@dataclass
class DataProvider:
    data_repo: IDataRepo

    def get_list_of_studies(self):
        return self.data_repo.get_list_of_studies()
