from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Optional


class Modes(IntEnum):
    antares = 1
    xpansion_r = 2
    xpansion_cpp = 3


@dataclass
class StudyDTO:
    """Study Data Transfer Object"""

    path: str
    name: str = field(init=False)
    zipfile_path: str = ""
    zip_is_sent: bool = False
    started: bool = False
    finished: bool = False
    with_error: bool = False
    local_final_zipfile_path: str = ""
    input_zipfile_removed: bool = False
    logs_downloaded: bool = False
    job_log_dir: str = ""
    output_dir: str = ""
    remote_server_is_clean: bool = False
    final_zip_extracted: bool = False
    done: bool = False
    job_id: Optional[int] = None
    job_state: str = ""
    time_limit: Optional[int] = None
    n_cpu: Optional[int] = None
    antares_version: Optional[str] = None
    xpansion_mode: Optional[str] = None
    run_mode: Modes = Modes.antares
    post_processing: bool = False
    other_options: str = ""

    def __post_init__(self):
        self.name = Path(self.path).name
