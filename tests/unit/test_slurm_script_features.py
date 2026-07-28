import pytest

from datetime import datetime, timedelta, timezone
from unittest import mock

from antareslauncher.remote_environnement.slurm_script_features import format_slurm_begin

FROZEN_NOW = datetime(2026, 7, 28, 12, 0, 0)


def _patch_now():
    return mock.patch(
        "antareslauncher.remote_environnement.slurm_script_features.current_time",
        return_value=FROZEN_NOW,
    )


@pytest.mark.unit_test
def test_format_slurm_begin_none_returns_none():
    assert format_slurm_begin(None) is None


@pytest.mark.unit_test
def test_format_slurm_begin_returns_relative_offset_in_minutes():
    with _patch_now():
        assert format_slurm_begin(FROZEN_NOW + timedelta(minutes=30)) == "now+30minutes"


@pytest.mark.unit_test
def test_format_slurm_begin_rounds_partial_minute_up():
    # +90s must never schedule earlier than run_at -> ceil to 2 minutes
    with _patch_now():
        assert format_slurm_begin(FROZEN_NOW + timedelta(seconds=90)) == "now+2minutes"


@pytest.mark.unit_test
def test_format_slurm_begin_past_time_clamped_to_now():
    # a run_at in the past means "start ASAP", never a negative offset
    with _patch_now():
        assert format_slurm_begin(FROZEN_NOW - timedelta(minutes=10)) == "now+0minutes"
