from unittest import mock

import pytest

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.use_cases.wait_loop_controller.wait_controller import (
    WaitController,
)


class TestWaitController:
    @pytest.mark.unit_test
    def test_countdown_calls_display_message_4_times_if_it_waits_1_seconds(
        self,
    ):
        display = IDisplay
        display.show_message = mock.Mock()
        display.show_message_no_newline = mock.Mock()
        wait_controller = WaitController(display)
        wait_controller.countdown(1)
        assert display.show_message.call_count == 4
