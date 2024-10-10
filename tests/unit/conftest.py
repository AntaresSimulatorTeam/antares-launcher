import shutil
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.use_cases.create_list.study_list_composer import StudyListComposer, StudyListComposerParameters
from tests.unit.assets import ASSETS_DIR
from antares.study.version import SolverMinorVersion


@pytest.fixture(name="studies_in_dir")
def studies_in_dir_fixture(tmp_path: Path) -> str:
    studies_in_dir = tmp_path.joinpath("STUDIES-IN")
    assets_dir = ASSETS_DIR.joinpath("study_list_composer/studies")
    shutil.copytree(assets_dir, studies_in_dir)
    return str(studies_in_dir)


@pytest.fixture(name="repo")
def repo_fixture(tmp_path: Path) -> DataRepoTinydb:
    return DataRepoTinydb(
        database_file_path=tmp_path.joinpath("repo.json"),
        db_primary_key="name",
    )


@pytest.fixture(name="study_list_composer")
def study_list_composer_fixture(
    tmp_path: Path,
    repo: DataRepoTinydb,
    studies_in_dir: str,
) -> StudyListComposer:
    display = mock.Mock(spec=DisplayTerminal)
    composer = StudyListComposer(
        repo=repo,
        display=display,
        parameters=StudyListComposerParameters(
            studies_in_dir=studies_in_dir,
            time_limit=42,
            n_cpu=24,
            log_dir=str(tmp_path.joinpath("LOGS")),
            xpansion_mode="",
            output_dir=str(tmp_path.joinpath("FINISHED")),
            post_processing=False,
            antares_versions_on_remote_server=[SolverMinorVersion.parse(v) for v in [
                "800",
                "810",
                "820",
                "830",
                "840",
                "850",
            ]],
            other_options="",

        ),
    )
    return composer
