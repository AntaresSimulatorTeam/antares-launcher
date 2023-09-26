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
