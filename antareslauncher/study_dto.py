import typing as t
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from antares.study.version import StudyVersion

class Modes(IntEnum):
    antares = 1
    xpansion_r = 2
    xpansion_cpp = 3


@dataclass
class StudyDTO:
    """Study Data Transfer Object"""

    path: str
    name: str = field(init=False)

    # Job state flags
    started: bool = False
    finished: bool = False
    done: bool = False
    with_error: bool = False

    # Job state message
    job_state: str = "Pending"  # "Running", "Finished", "Ended with error", "Internal error: ..."

    # Processing stage flags
    zip_is_sent: bool = False
    input_zipfile_removed: bool = False
    logs_downloaded: bool = False
    remote_server_is_clean: bool = False
    final_zip_extracted: bool = False

    # Processing stage data
    job_id: int = 0  # sbatch job id
    zipfile_path: str = ""
    local_final_zipfile_path: str = ""
    job_log_dir: str = ""
    output_dir: str = ""

    # Simulation stage data
    time_limit: t.Optional[int] = None
    n_cpu: int = 1
    antares_version: StudyVersion = StudyVersion.parse(0)
    xpansion_mode: str = ""  # "", "r", "cpp"
    run_mode: Modes = Modes.antares
    post_processing: bool = False
    other_options: str = ""

    def __post_init__(self) -> None:
        self.name = Path(self.path).name

    @classmethod
    def from_dict(cls, doc: t.Mapping[str, t.Any]) -> "StudyDTO":
        """
        Create a Study DTO from a mapping.
        """
        attrs = dict(**doc)
        attrs.pop("name", None)  # calculated
        attrs["antares_version"] = StudyVersion.parse(attrs["antares_version"])
        return cls(**attrs)
