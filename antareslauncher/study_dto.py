from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Optional


class Modes(IntEnum):
    antares = 1
    xpansion = 2


@dataclass
class StudyDTO:
    """Study Data Transfer Object"""

    path: str
    name: str = field(init=False)
    zipfile_path: Optional[str] = ""
    zip_is_sent: Optional[bool] = False
    started: Optional[bool] = False
    finished: Optional[bool] = False
    with_error: Optional[bool] = False
    local_final_zipfile_path: Optional[str] = ""
    input_zipfile_removed: Optional[bool] = False
    logs_downloaded: Optional[bool] = False
    job_log_dir: Optional[str] = ""
    output_dir: Optional[str] = ""
    remote_server_is_clean: Optional[bool] = False
    final_zip_extracted: Optional[bool] = False
    done: Optional[bool] = False
    job_id: Optional[int] = None
    job_state: Optional[str] = ""
    time_limit: Optional[int] = None
    n_cpu: Optional[int] = None
    antares_version: Optional[int] = None
    xpansion_study: Optional[bool] = False
    run_mode: Optional[Modes] = Modes.antares
    post_processing: Optional[bool] = False

    def __post_init__(self):
        self.name = Path(self.path).name
