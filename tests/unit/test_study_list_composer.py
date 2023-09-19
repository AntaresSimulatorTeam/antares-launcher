import shutil
from pathlib import Path
from unittest import mock

import pytest
from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.use_cases.create_list.study_list_composer import (
    StudyListComposer,
    get_solver_version,
    StudyListComposerParameters,
)
from unit.assets import ASSETS_DIR

CONFIG_NOMINAL_VERSION = """\
[antares]
version = 800
caption = Sample Study
created = 1688740888
lastsave = 1688740888
author = john.doe
"""

CONFIG_NOMINAL_SOLVER_VERSION = """\
[antares]
version = 800
caption = Sample Study
created = 1688740888
lastsave = 1688740888
author = john.doe
solver_version = 850
"""

CONFIG_MISSING_SECTION = """\
[polaris]
version = 800
caption = Sample Study
created = 1688740888
lastsave = 1688740888
author = john.doe
"""

CONFIG_MISSING_VERSION = """\
[antares]
caption = Sample Study
created = 1688740888
lastsave = 1688740888
author = john.doe
"""


class TestGetSolverVersion:
    @pytest.mark.parametrize(
        "config_ini, expected",
        [
            pytest.param(CONFIG_NOMINAL_VERSION, 800, id="with_version"),
            pytest.param(CONFIG_NOMINAL_SOLVER_VERSION, 850, id="with_solver_version"),
            pytest.param(CONFIG_MISSING_SECTION, 999, id="bad_missing_section"),
            pytest.param(CONFIG_MISSING_VERSION, 999, id="bad_missing_version"),
        ],
    )
    def test_get_solver_version(
        self,
        config_ini: str,
        expected: int,
        tmp_path: Path,
    ) -> None:
        study_path = tmp_path.joinpath("study.antares")
        study_path.write_text(config_ini, encoding="utf-8")
        actual = get_solver_version(tmp_path, default=999)
        assert actual == expected


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
        file_manager=FileManager(display_terminal=display),
        display=display,
        parameters=StudyListComposerParameters(
            studies_in_dir=studies_in_dir,
            time_limit=42,
            n_cpu=24,
            log_dir=str(tmp_path.joinpath("LOGS")),
            xpansion_mode=None,
            output_dir=str(tmp_path.joinpath("FINISHED")),
            post_processing=False,
            antares_versions_on_remote_server=[
                "800",
                "810",
                "820",
                "830",
                "840",
                "850",
            ],
            other_options="",
        ),
    )
    return composer


class TestStudyListComposer:
    @pytest.mark.parametrize("xpansion_mode", ["r", "cpp", ""])
    def test_update_study_database__xpansion_mode(
        self,
        study_list_composer: StudyListComposer,
        xpansion_mode: str,
    ):
        study_list_composer.xpansion_mode = xpansion_mode
        study_list_composer.update_study_database()
        studies = study_list_composer.get_list_of_studies()

        # check the found studies
        actual_names = {s.name for s in studies}
        expected_names = {
            "": {
                "013 TS Generation - Solar power",
                "024 Hurdle costs - 1",
                "SMTA-case",
            },
            "r": {"SMTA-case"},
            "cpp": {"SMTA-case"},
        }[study_list_composer.xpansion_mode or ""]
        assert actual_names == expected_names

    @pytest.mark.parametrize("antares_version", [0, 850, 990])
    def test_update_study_database__antares_version(
        self,
        study_list_composer: StudyListComposer,
        antares_version: int,
    ):
        study_list_composer.antares_version = antares_version
        study_list_composer.update_study_database()
        studies = study_list_composer.get_list_of_studies()

        # check the versions
        actual_versions = {s.name: s.antares_version for s in studies}
        if antares_version == 0:
            expected_versions = {
                "013 TS Generation - Solar power": 850,  # solver_version
                "024 Hurdle costs - 1": 840,  # versions
                "SMTA-case": 810,  # version
            }
        elif antares_version in study_list_composer.ANTARES_VERSIONS_ON_REMOTE_SERVER:
            study_names = {
                "013 TS Generation - Solar power",
                "024 Hurdle costs - 1",
                "069 Hydro Reservoir Model",
                "BAD Study Section",
                "MISSING Study version",
                "SMTA-case",
            }
            expected_versions = dict.fromkeys(study_names, antares_version)
        else:
            expected_versions = {}
        assert {n: expected_versions[n] for n in actual_versions} == actual_versions
