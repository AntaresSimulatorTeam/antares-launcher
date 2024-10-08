from pathlib import Path

import pytest

from antareslauncher.use_cases.create_list.study_list_composer import StudyListComposer, get_solver_version
from antares.study.version import SolverMinorVersion

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
        parsed_version = SolverMinorVersion.parse(antares_version)
        study_list_composer.antares_version = parsed_version
        study_list_composer.update_study_database()
        studies = study_list_composer.get_list_of_studies()

        # check the versions
        actual_versions = {s.name: s.antares_version for s in studies}
        if antares_version == 0:
            expected_versions = {
                "013 TS Generation - Solar power": "8.5",  # solver_version
                "024 Hurdle costs - 1": "8.4",  # versions
                "SMTA-case": "8.1",  # version
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
            expected_versions = dict.fromkeys(study_names, parsed_version)
        else:
            expected_versions = {}
        assert actual_versions == {n: expected_versions[n] for n in actual_versions}
