import datetime
import logging
import typing as t

from tqdm import tqdm


class DisplayTerminal:
    def __init__(self) -> None:
        # Use the ISO8601 date format to display messages on the console
        self.format = "%Y-%m-%d %H:%M:%S%z"

    def show_message(self, message: str, class_name: str, end: str = "\n") -> None:
        """Displays a message on the terminal

        Args:
            message: String containing the message to display
            class_name: name of the class calling the class for logging
            end: end of the line for the print statement
        """
        now = datetime.datetime.now()
        print(f"[{now.strftime(self.format)}] " + message, end=end)
        if end != "\r":
            logging.getLogger(class_name).info(message)

    def show_error(self, error: str, class_name: str) -> None:
        """Displays a error on the terminal

        Args:
            error: String containing the error to display
            class_name: name of the class calling the class for logging
        """
        now = datetime.datetime.now()
        print(f"ERROR - [{now.strftime(self.format)}] " + error)
        logging.getLogger(class_name).error(error)

    def generate_progress_bar(
        self,
        iterator: t.Iterable[t.Any],
        desc: str = "",
        total: t.Optional[int] = None,
    ) -> t.Iterable[t.Any]:
        """Generates al loading bar and shows it in the terminal

        Args:
            iterator: iterator to explore
            desc: Prefix for the progress bar
            total: Total number of elements in the iterator

        Returns:
            iterator that displays a progress bar
        """

        now = datetime.datetime.now()
        progress_bar = tqdm(
            iterator,
            total=total,
            desc=desc,
            leave=False,
            dynamic_ncols=True,
            bar_format="[" + str(now.strftime(self.format)) + "] {l_bar}{bar}| {n_fmt}/{total_fmt} ",
        )
        return progress_bar
