import copy

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.study_dto import StudyDTO


class FinalZipNotDownloadedException(Exception):
    pass


class FinalZipDownloader(object):
    def __init__(
        self,
        env: iremote_environment.IRemoteEnvironment,
        display: IDisplay,
    ):
        self._env = env
        self._display = display
        self._current_study = None

    def download(self, study: StudyDTO):
        """
        Download the final ZIP file for the specified study, if it has finished
        (without error) and has not been downloaded yet.

        Args:
            study: A data transfer object representing the study to download.

        Returns:
            The updated data transfer object, with its `local_final_zipfile_path`
            attribute set if the download was successful.

        Raises:
            FinalZipNotDownloadedException: If the download fails or no files are found.
        """
        self._current_study = copy.copy(study)
        if (
            self._current_study.finished
            and not self._current_study.with_error
            and not self._current_study.local_final_zipfile_path
        ):
            self._do_download()
        return self._current_study

    def _do_download(self):
        """
        Perform the download of the final ZIP file for the current study,
        and update its `local_final_zipfile_path` attribute.

        Raises:
            FinalZipNotDownloadedException: If the download fails or no files are found.

        Note:
            This function delegates the download operation to the
            `_env.download_final_zip` method, which is assumed to return
            the path to the downloaded zip file on the local filesystem
            or `None` if the download fails or no files are found.

            If the download succeeds, the `local_final_zipfile_path` attribute
            of the `_current_study` object is updated with the path to the
            downloaded file, and a success message is displayed.

            If the download fails, an error message is displayed and a
            `FinalZipNotDownloadedException` exception is raised.
        """
        self._display.show_message(
            f'"{self._current_study.name}": downloading final ZIP...',
            f"{__name__}.{__class__.__name__}",
        )
        if local_final_zipfile_path := self._env.download_final_zip(
            copy.copy(self._current_study)
        ):
            self._current_study.local_final_zipfile_path = str(local_final_zipfile_path)
            self._display.show_message(
                f'"{self._current_study.name}": Final ZIP downloaded',
                f"{__name__}.{__class__.__name__}",
            )
        else:
            self._display.show_error(
                f'"{self._current_study.name}": Final ZIP not downloaded',
                f"{__name__}.{__class__.__name__}",
            )
            raise FinalZipNotDownloadedException(
                self._current_study.local_final_zipfile_path
            )
