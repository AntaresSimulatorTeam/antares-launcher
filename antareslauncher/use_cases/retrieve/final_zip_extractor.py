import os.path
import zipfile
from pathlib import Path

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.study_dto import StudyDTO

LOG_NAME = f"{__name__}.FinalZipDownloader"


class FinalZipExtractor:
    def __init__(self, display: DisplayTerminal):
        self._display = display

    def extract_final_zip(self, study: StudyDTO) -> None:
        """
        Extracts the simulation results, which are in the form of a ZIP file,
        after it has been downloaded from Antares.

        Args:
            study: The current study
        """
        if not study.finished or not study.local_final_zipfile_path or study.final_zip_extracted:
            return
        zip_path = Path(study.local_final_zipfile_path)
        try:
            # First, we detect the ZIP layout by looking at the names of the files it contains.
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
                file_count = len(names)
                has_unique_folder = file_count > 1 and os.path.commonpath(names)

            if has_unique_folder:
                # If the ZIP file contains a unique folder, it contains the whole study.
                # We can extract it directly in the target directory.
                with zipfile.ZipFile(zip_path) as zf:
                    target_dir = zip_path.parent
                    progress_bar = self._display.generate_progress_bar(
                        names, desc="Extracting archive:", total=file_count
                    )
                    for file in progress_bar:
                        zf.extract(member=file, path=target_dir)

            else:
                # The directory is already an output and does not need to be unzipped.
                # All we have to do is rename it by removing the prefix "finished_"
                # and the suffix "_{job_id}" that lies before the ".zip".
                # e.g.: "finished_Foo-Study_123456.zip" -> "Foo-Study.zip".
                # or:   "finished_XPANSION_Foo-Study_123456.zip" -> "Foo-Study_123456.zip".
                new_name = zip_path.name.lstrip("finished_")
                new_name = new_name.lstrip("XPANSION_")
                new_name = new_name.split("_", 1)[0] + ".zip"
                zip_path.rename(zip_path.parent / new_name)

        except (OSError, zipfile.BadZipFile) as exc:
            # If we cannot extract the final ZIP file, either because the file
            # doesn't exist or the ZIP file is corrupted, we find ourselves
            # in a situation where the results are unusable.
            # In such cases, it's best to consider the simulation as failed,
            # enabling the user to restart its simulation.
            study.final_zip_extracted = False
            study.with_error = True
            self._display.show_error(
                f'"{study.name}": Final zip not extracted: {exc}',
                LOG_NAME,
            )

        else:
            study.final_zip_extracted = True
            self._display.show_message(
                f'"{study.name}": Final zip extracted',
                LOG_NAME,
            )
