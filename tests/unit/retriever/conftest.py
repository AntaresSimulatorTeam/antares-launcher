import dataclasses
from pathlib import Path

import pytest

from antareslauncher.study_dto import StudyDTO


@pytest.fixture(name="pending_study")
def pending_study_fixture(tmp_path: Path) -> StudyDTO:
    study_path = tmp_path.joinpath("My Study")
    job_log_dir = tmp_path.joinpath("LOG_DIR")
    output_dir = tmp_path.joinpath("OUTPUT_DIR")
    return StudyDTO(
        path=str(study_path),
        started=False,
        job_log_dir=str(job_log_dir),
        output_dir=str(output_dir),
        zipfile_path="",
        zip_is_sent=False,
        job_id=0,
    )


@pytest.fixture(name="started_study")
def started_study_fixture(pending_study: StudyDTO) -> StudyDTO:
    study_dir = Path(pending_study.path)
    zip_name = f"{study_dir.name}-john_doe.zip"
    zip_path = study_dir.parent / zip_name
    return dataclasses.replace(
        pending_study,
        started=True,
        finished=False,
        with_error=False,
        zipfile_path=str(zip_path),
        zip_is_sent=True,
        job_id=46505574,
    )


@pytest.fixture(name="finished_study")
def finished_study_fixture(started_study: StudyDTO) -> StudyDTO:
    return dataclasses.replace(started_study, finished=True, with_error=False)


@pytest.fixture(name="with_error_study")
def with_error_study_fixture(started_study: StudyDTO) -> StudyDTO:
    return dataclasses.replace(started_study, finished=True, with_error=True)
