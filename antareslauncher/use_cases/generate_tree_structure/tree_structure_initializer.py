from dataclasses import dataclass
from pathlib import Path

from antareslauncher.display.display_terminal import DisplayTerminal


@dataclass
class TreeStructureInitializer:
    display: DisplayTerminal
    studies_in: str
    log_dir: str
    output_dir: str

    def init_tree_structure(self):
        """Initialize the structure"""
        Path(self.studies_in).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.display.show_message("Tree structure initialized", __name__ + "." + __class__.__name__)
