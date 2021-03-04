import sys

from antareslauncher.main import run_with
from antareslauncher.main_option_parser import MainOptionParser

if __name__ == "__main__":
    parser: MainOptionParser = MainOptionParser()
    parser.add_basic_arguments()
    parser.add_advanced_arguments()
    arguments = parser.parse_args()
    run_with(arguments)
    if not len(sys.argv) > 1:
        input("Press ENTER to exit.")
