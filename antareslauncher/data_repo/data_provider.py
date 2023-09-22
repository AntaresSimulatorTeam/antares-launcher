from dataclasses import dataclass

from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb


@dataclass
class DataProvider:
    data_repo: DataRepoTinydb

    def get_list_of_studies(self):
        return self.data_repo.get_list_of_studies()
