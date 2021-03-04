import time
from dataclasses import dataclass

from antareslauncher.display.idisplay import IDisplay


@dataclass
class WaitController:
    display: IDisplay

    def countdown(self, seconds_to_wait: int):
        """
        Start a wait loop that last `seconds_to_wait`.

        It prints every second a countdown rolling string
        using display.message_with_no_newline

        Args:
            seconds_to_wait: number of seconds to wait
        """
        initial_message = "Start of the wait loop.                           "
        self.display.show_message(initial_message, __name__)

        self._wait_loop(seconds_to_wait)
        final_message = "Wait loop is finished.                           "
        self.display.show_message(final_message, __name__)

    def _wait_loop(self, seconds_to_wait: int) -> None:
        """
        executes the wait loop for the public function `countdown`

        Args:
            seconds_to_wait: number of seconds to wait
        """
        seconds_between_messages = 1
        text_4_countdown = "End of loop in ... "
        while seconds_to_wait >= 0:
            mins, secs = divmod(seconds_to_wait, 60)
            formatted_time = "{:02d}:{:02d}".format(mins, secs)

            self.display.show_message(
                text_4_countdown + formatted_time, __name__, end="\r"
            )
            time.sleep(seconds_between_messages)
            seconds_to_wait -= seconds_between_messages
