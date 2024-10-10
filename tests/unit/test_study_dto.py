from antares.study.version import StudyVersion

from antareslauncher.study_dto import StudyDTO


def test_study_dto_from_dict_old_version_syntax():

    study_dict = {
        "path": "/path/to/study",
        "antares_version": 880
    }

    study_dto = StudyDTO.from_dict(study_dict)
    assert study_dto.antares_version == StudyVersion.parse("8.8")


def test_study_dto_from_dict():
    study_dict = {
        "path": "/path/to/study",
        "antares_version": "9.0"
    }
    study_dto = StudyDTO.from_dict(study_dict)
    assert study_dto.antares_version == StudyVersion.parse("9.0")
