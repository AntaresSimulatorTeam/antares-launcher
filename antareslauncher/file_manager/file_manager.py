import json
import logging
import os

from antareslauncher.display.display_terminal import DisplayTerminal


class FileManager:
    def __init__(self, display_terminal: DisplayTerminal):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.display = display_terminal

    def make_dir(self, directory_name):
        self.logger.info(f"Creating directory {directory_name}")
        os.makedirs(directory_name, exist_ok=True)

    def convert_json_file_to_dict(self, file_path):
        self.logger.info(f"Converting json file {file_path} to dict")
        try:
            with open(file_path, "r") as readFile:
                config = json.load(readFile)
        except OSError:
            self.logger.error(f"Unable to convert {file_path} to json (file not found or invalid type)")
            config = None
        return config
