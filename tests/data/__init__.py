"""
Manage access to the unit test resource data directory.
"""
from pathlib import Path

# Full path to the resource data directory used in unit tests.
DATA_DIR: Path = Path(__file__).parent.resolve()
