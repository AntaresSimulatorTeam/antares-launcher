from dataclasses import dataclass

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager


@dataclass
class TreeStructureInitializer:
    display: IDisplay
    file_manager: FileManager
    studies_in: str
    log_dir: str
    finished: str

    def init_tree_structure(self):
        """Initialize the structure"""
        self.file_manager.make_dir(self.studies_in)
        self.file_manager.make_dir(self.log_dir)
        self.file_manager.make_dir(self.finished)
        self.display.show_message(
            "Tree structure initialized", __name__ + "." + __class__.__name__
        )
