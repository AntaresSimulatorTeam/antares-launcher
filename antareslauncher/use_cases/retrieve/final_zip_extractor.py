from pathlib import Path

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.study_dto import StudyDTO


class ResultNotExtractedException(Exception):
    pass


class FinalZipExtractor:
    def __init__(self, file_manager: FileManager, display: IDisplay):
        self._file_manager = file_manager
        self._display = display
        self._current_study: StudyDTO = None

    def extract_final_zip(self, study: StudyDTO) -> StudyDTO:
        self._current_study = study
        if self._study_final_zip_should_be_extracted():
            self._do_extract()
        return self._current_study

    def _do_extract(self):
        zipfile_to_extract = self._current_study.local_final_zipfile_path
        success = self._file_manager.unzip(zipfile_to_extract)
        if success:
            self._current_study.final_zip_extracted = success
            self._show_success_message()
        else:
            self._show_failure_error()
            raise ResultNotExtractedException

    def _show_failure_error(self):
        self._display.show_error(
            f'"{Path(self._current_study.path).name}": Final zip not extracted',
            __name__ + "." + __class__.__name__,
        )

    def _show_success_message(self):
        self._display.show_message(
            f'"{Path(self._current_study.path).name}": Final zip extracted',
            __name__ + "." + __class__.__name__,
        )

    def _study_final_zip_should_be_extracted(self):
        return (
            self._current_study.local_final_zipfile_path
            and not self._current_study.final_zip_extracted
        )
