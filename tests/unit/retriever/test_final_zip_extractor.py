import dataclasses
import zipfile
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.final_zip_extractor import FinalZipExtractor


def create_final_zip(study: StudyDTO, *, scenario: str = "nominal_study") -> str:
    """Prepare a final ZIP."""
    dst_dir = Path(study.output_dir)  # must exist
    dst_dir.mkdir(parents=True, exist_ok=True)
    if "xpansion" in scenario:
        out_path = dst_dir.joinpath(f"finished_XPANSION_{study.name}_{study.job_id}.zip")
    else:
        out_path = dst_dir.joinpath(f"finished_{study.name}_{study.job_id}.zip")
    if scenario in {"nominal_study", "xpansion_study"}:
        # Case where the ZIP contains all the study files.
        with zipfile.ZipFile(
            out_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zf:
            zf.writestr(
                f"{study.name}/input/study.antares",
                data=b"[antares]\nversion = 860\n",
            )
            zf.writestr(
                f"{study.name}/output/20230922-1601eco/simulation.log",
                data=b"Simulation OK",
            )
    elif scenario in {"nominal_results", "xpansion_results"}:
        # Case where the ZIP contains only the results.
        with zipfile.ZipFile(
            out_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zf:
            zf.writestr("simulation.log", data=b"Simulation OK")
    elif scenario == "corrupted":
        # Case where the ZIP is corrupted.
        out_path.write_bytes(b"PK corrupted content")
    elif scenario == "missing":
        # Case where the ZIP is missing.
        pass
    else:
        raise NotImplementedError(scenario)
    return str(out_path)


class TestFinalZipExtractor:
    @pytest.mark.unit_test
    def test_extract_final_zip__pending_study(self, pending_study: StudyDTO) -> None:
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the ZIP extraction
        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(pending_study)

        # Check the result
        display.show_message.assert_not_called()
        display.show_error.assert_not_called()
        assert not pending_study.final_zip_extracted

    @pytest.mark.unit_test
    def test_extract_final_zip__started_study(self, started_study: StudyDTO) -> None:
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the ZIP extraction
        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(started_study)

        # Check the result
        display.show_message.assert_not_called()
        display.show_error.assert_not_called()
        assert not started_study.final_zip_extracted

    @pytest.mark.unit_test
    def test_extract_final_zip__finished_study__no_output(self, finished_study: StudyDTO) -> None:
        display = mock.Mock(spec=DisplayTerminal)

        # Initialize and execute the ZIP extraction
        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(finished_study)

        # Check the result
        display.show_message.assert_not_called()
        display.show_error.assert_not_called()
        assert not finished_study.final_zip_extracted

    @pytest.mark.unit_test
    @pytest.mark.parametrize("scenario", ["nominal_study", "xpansion_study"])
    def test_extract_final_zip__finished_study__nominal_study(self, finished_study: StudyDTO, scenario: str) -> None:
        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = lambda names, *args, **kwargs: names

        # Prepare a valid final ZIP
        finished_study.local_final_zipfile_path = create_final_zip(finished_study, scenario=scenario)

        # Initialize and execute the ZIP extraction
        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(finished_study)

        # Check the result
        display.show_message.assert_called_once()
        display.show_error.assert_not_called()

        assert finished_study.final_zip_extracted
        assert not finished_study.with_error

        result_dir = Path(finished_study.output_dir).joinpath(finished_study.name)
        expected_files = [
            "input/study.antares",
            "output/20230922-1601eco/simulation.log",
        ]
        for file in expected_files:
            assert result_dir.joinpath(file).is_file()

    @pytest.mark.unit_test
    @pytest.mark.parametrize("scenario", ["nominal_results", "xpansion_results"])
    def test_extract_final_zip__finished_study__nominal_results(self, finished_study: StudyDTO, scenario: str) -> None:
        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = lambda names, *args, **kwargs: names

        # Prepare a valid final ZIP
        finished_study.local_final_zipfile_path = create_final_zip(finished_study, scenario=scenario)

        # Initialize and execute the ZIP extraction
        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(finished_study)

        # Check the result
        display.show_message.assert_called_once()
        display.show_error.assert_not_called()

        assert finished_study.final_zip_extracted
        assert not finished_study.with_error

        result_dir = (Path(finished_study.local_final_zipfile_path).parent / finished_study.name).with_suffix(".zip")
        assert result_dir.exists()
        with zipfile.ZipFile(result_dir, "r") as zf:
            assert zf.namelist() == ["simulation.log"]

    @pytest.mark.unit_test
    @pytest.mark.parametrize("scenario", ["nominal_study", "xpansion_study"])
    def test_extract_final_zip__finished_study__reentrancy(self, finished_study: StudyDTO, scenario: str) -> None:
        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = lambda names, *args, **kwargs: names

        # Prepare a valid final ZIP
        finished_study.local_final_zipfile_path = create_final_zip(finished_study, scenario=scenario)

        # Initialize and execute the ZIP extraction twice
        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(finished_study)
        study_state1 = dataclasses.asdict(finished_study)

        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(finished_study)
        study_state2 = dataclasses.asdict(finished_study)

        assert study_state1 == study_state2

    @pytest.mark.unit_test
    def test_extract_final_zip__finished_study__missing(self, finished_study: StudyDTO) -> None:
        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = lambda names, *args, **kwargs: names

        # Prepare a missing final ZIP
        finished_study.local_final_zipfile_path = create_final_zip(finished_study, scenario="missing")

        # Initialize and execute the ZIP extraction
        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(finished_study)

        # Check the result
        display.show_message.assert_not_called()
        display.show_error.assert_called_once()

        assert not finished_study.final_zip_extracted
        assert finished_study.with_error

        result_dirs = [
            Path(finished_study.output_dir).joinpath(finished_study.name),
            Path(finished_study.local_final_zipfile_path).with_suffix(""),
        ]
        assert not any(result_dir.exists() for result_dir in result_dirs)

    @pytest.mark.unit_test
    def test_extract_final_zip__finished_study__corrupted(self, finished_study: StudyDTO) -> None:
        display = mock.Mock(spec=DisplayTerminal)
        display.generate_progress_bar = lambda names, *args, **kwargs: names

        # Prepare a corrupted final ZIP
        finished_study.local_final_zipfile_path = create_final_zip(finished_study, scenario="corrupted")

        # Initialize and execute the ZIP extraction
        extractor = FinalZipExtractor(display=display)
        extractor.extract_final_zip(finished_study)

        # Check the result
        display.show_message.assert_not_called()
        display.show_error.assert_called_once()

        assert not finished_study.final_zip_extracted
        assert finished_study.with_error

        result_dirs = [
            Path(finished_study.output_dir).joinpath(finished_study.name),
            Path(finished_study.local_final_zipfile_path).with_suffix(""),
        ]
        assert not any(result_dir.exists() for result_dir in result_dirs)
