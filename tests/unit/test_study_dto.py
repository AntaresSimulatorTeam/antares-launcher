from datetime import datetime

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


def test_study_dto_from_dict_default_run_at():
    # old records lacking a "run_at" key must still load
    study_dict = {"path": "/path/to/study", "antares_version": "9.0"}
    study_dto = StudyDTO.from_dict(study_dict)
    assert study_dto.run_at is None


def test_study_dto_run_at_round_trips_through_from_dict():
    # run_at is stored as an ISO-8601 string in the database and parsed back to a datetime
    study_dict = {"path": "/path/to/study", "antares_version": "9.0", "run_at": "2026-07-04T19:00:00"}
    study_dto = StudyDTO.from_dict(study_dict)
    assert study_dto.run_at == datetime(2026, 7, 4, 19, 0, 0)
