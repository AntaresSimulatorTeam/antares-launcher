import copy
import getpass
from dataclasses import dataclass
from pathlib import Path

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.study_dto import StudyDTO


@dataclass
class StudyZipper:
    def __init__(self, file_manager: FileManager, display: IDisplay):
        self.file_manager = file_manager
        self.display = display
        self._current_study: StudyDTO = None

    def zip(self, study) -> StudyDTO:
        self._current_study = copy.deepcopy(study)

        if study.zipfile_path == "":
            self._do_zip()
        return self._current_study

    def _do_zip(self):
        zipfile_path = self._current_study.path + "-" + getpass.getuser() + ".zip"
        success = self.file_manager.zip_dir_excluding_subdir(
            self._current_study.path, zipfile_path, "output"
        )
        if success is True:
            self._current_study.zipfile_path = zipfile_path
            self._display_success_message()
        else:
            self._display_failure_error()

    def _display_failure_error(self):
        self.display.show_error(
            f'"{Path(self._current_study.path).name}": was not zipped',
            __name__ + "." + __class__.__name__,
        )

    def _display_success_message(self):
        self.display.show_message(
            f'"{Path(self._current_study.path).name}": was zipped',
            __name__ + "." + __class__.__name__,
        )
