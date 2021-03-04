import copy

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.study_dto import StudyDTO


class StudyZipCleaner:
    def __init__(self, file_manager: FileManager, display: IDisplay):
        self.file_manager = file_manager
        self.display = display
        self._current_study: StudyDTO = StudyDTO("none")

    def remove_input_zipfile(self, study: StudyDTO) -> StudyDTO:
        self._current_study = copy.deepcopy(study)
        self.file_manager.remove_file(self._current_study.zipfile_path)
        return self._current_study
