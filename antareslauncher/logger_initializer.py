import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler


@dataclass
class LoggerInitializer:
    file_path: str

    def init_logger(self):
        """
        Initialise the logger with predefined  formats and logging.level
        Returns:

        """
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        f_handler = RotatingFileHandler(
            self.file_path, maxBytes=200000, backupCount=5, mode="a+"
        )
        f_handler.setFormatter(formatter)
        f_handler.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.INFO, handlers=[f_handler])
