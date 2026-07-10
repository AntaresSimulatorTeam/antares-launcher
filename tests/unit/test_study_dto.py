from antares.study.version import StudyVersion

from antareslauncher.study_dto import StudyDTO


def test_study_dto_from_dict_old_version_syntax():
    study_dict = {"path": "/path/to/study", "antares_version": 880}

    study_dto = StudyDTO.from_dict(study_dict)
    assert study_dto.antares_version == StudyVersion.parse("8.8")


def test_study_dto_from_dict():
    study_dict = {"path": "/path/to/study", "antares_version": "9.0"}
    study_dto = StudyDTO.from_dict(study_dict)
    assert study_dto.antares_version == StudyVersion.parse("9.0")


def test_study_dto_from_dict_default_begin():
    # old records lacking a "begin" key must still load
    study_dict = {"path": "/path/to/study", "antares_version": "9.0"}
    study_dto = StudyDTO.from_dict(study_dict)
    assert study_dto.begin == ""


def test_study_dto_begin_round_trips_through_from_dict():
    study_dict = {"path": "/path/to/study", "antares_version": "9.0", "begin": "2026-07-04T19:00:00"}
    study_dto = StudyDTO.from_dict(study_dict)
    assert study_dto.begin == "2026-07-04T19:00:00"
