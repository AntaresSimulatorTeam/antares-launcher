import getpass
import zipfile
from pathlib import Path

from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.use_cases.launch.study_submitter import StudySubmitter
from antareslauncher.use_cases.launch.study_zip_uploader import StudyZipfileUploader

LOG_NAME = f"{__name__}.StudyLauncher"


class StudyLauncher:
    def __init__(
        self,
        study_uploader: StudyZipfileUploader,
        study_submitter: StudySubmitter,
        reporter: DataReporter,
        display: DisplayTerminal,
    ):
        self.display = display
        self._study_uploader = study_uploader
        self._study_submitter = study_submitter
        self.reporter = reporter

    def launch_study(self, study):
        if study.job_id:
            # No need to display a user message here; job already exists.
            return

        try:
            # Compress the study folder and upload it to the SLURM server.
            study_dir = Path(study.path)
            zip_name = f"{study_dir.name}-{getpass.getuser()}.zip"
            root_dir = study_dir.parent
            zip_path = root_dir / zip_name

            # Find all files to be compressed.
            study_files = set(study_dir.rglob("*"))

            # NOTE: output filtering isn't currently handled.
            #
            # Antares Web sets up the study directory with pre-filtered outputs when launching,
            # but this isn't the case with the CLI.
            # We may introduce new parameters in `StudyDTO` for customizable output filtering
            # at the study level, especially for scenarios like Xpansion sensitivity mode.
            #
            # Suggested parameters:
            # - `exclude_pattern = "output/**/*"`: Default CLI exclusion.
            # - `include_pattern = "output/{output_id}/**/*"`: Inclusion for specific output
            #   for Xpansion sensitivity mode (e.g., `output_id = "20230926-1230adq"`).
            #
            # Suggested implementation:
            # study_files -= set(study_dir.glob(exclude_pattern)) if exclude_pattern else set()
            # study_files |= set(study_dir.glob(include_pattern)) if include_pattern else set()

            # Compress the study directory
            with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                loading_bar = self.display.generate_progress_bar(sorted(study_files), desc="Compressing files: ")
                for study_file in loading_bar:
                    zf.write(study_file, study_file.relative_to(root_dir))

            # Upload the ZIP file to the SLURM server.
            # If the upload is successful, the `zip_is_sent` attribute is updated accordingly.
            # In all cases, the ZIP file is removed from the local machine.
            study.zipfile_path = str(zip_path)
            try:
                self._study_uploader.upload(study)
                if not study.zip_is_sent:
                    raise Exception("ZIP upload failed")
            except Exception as e:
                self.display.show_error(f'"{study.name}": was not uploaded: {e}', LOG_NAME)
                # If the ZIP file is partially uploaded, it must be removed anyway.
                self._study_uploader.remove(study)
                raise
            finally:
                zip_path.unlink()

            # Now launch the job on the SLURM server.
            # If the launch is successful, the `job_id` attribute is updated accordingly.
            # If the launch fails, remove the ZIP file from the remote server.
            try:
                self._study_submitter.submit_job(study)
                if not study.job_id:
                    raise Exception("Job submission failed")
            except Exception:
                self._study_uploader.remove(study)
                raise

        except Exception as e:
            # The exception is not re-raised, but the job is marked as failed with an internal error message.
            study.with_error = True
            study.job_state = f"Internal error: {e}"

        finally:
            # Save the study information after processing.
            self.reporter.save_study(study)


class LaunchController:
    def __init__(
        self,
        repo: DataRepoTinydb,
        env: RemoteEnvironmentWithSlurm,
        display: DisplayTerminal,
    ):
        self.repo = repo
        self.env = env
        self.display = display
        study_uploader = StudyZipfileUploader(env, display)
        study_submitter = StudySubmitter(env, display)
        self.study_launcher = StudyLauncher(study_uploader, study_submitter, DataReporter(repo), display)

    def launch_all_studies(self):
        """Processes all the studies and send them to the server to process the job

        Steps of processing:

        1. zip the study

        2. upload the study

        3. submit the slurm job
        """
        studies = self.repo.get_list_of_studies()
        for study in studies:
            self.study_launcher.launch_study(study)
