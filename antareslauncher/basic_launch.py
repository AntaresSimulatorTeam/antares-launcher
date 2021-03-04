import sys

from antareslauncher import main
from antareslauncher.main_option_parser import MainOptionParser

if __name__ == "__main__":
    parser: MainOptionParser = MainOptionParser()
    parser.add_basic_arguments()
    input_arguments = parser.parse_args()
    main.run_with(input_arguments)
    if not len(sys.argv) > 1:
        input("Press ENTER to exit.")
