"""This file contains the CONSTANTS for ASL"""
import getpass
import json
from pathlib import Path

import yaml

"""
After a little bit of research. This is the standard way of doing things. 
We can categories the CONSTANTS if we want in some dictionaries, but otherwise, it is done the way it is in our code.

ex: 
database = dict(
    DATABASE = "mysql",
    USER     = "Lark",
    PASS     = ""
)
print(constants.database["DATABASE"])

------------------------------------------------------------------------------------------------------------------------

import constants

def use_my_constants():
    print constants.GOOD, constants.BAD, constants.AWFUL

From the python zen:

    Namespaces are good. Lets do more of those!

    Namespaces are one honking great idea -- let's do more of those!

I actually copied it from the source: PEP 20 -- The Zen of Python
"""


DATA_DIR = Path(__file__).parent.resolve() / ".." / "data"

# YAML:
LOG_DIR = None
STUDIES_IN_DIR = None
FINISHED_DIR = None
DEFAULT_TIME_LIMIT = None
DEFAULT_N_CPU = None
DEFAULT_WAIT_TIME = None
SLURM_SCRIPT_PATH = None
DB_PRIMARY_KEY = None
ANTARES_VERSIONS_ON_REMOTE_SERVER = None
DEFAULT_SSH_CONFIGFILE_NAME = None
SSH_CONFIG_FILE_IS_REQUIRED = None
DEFAULT_JSON_DB_NAME = f"{getpass.getuser()}_antares_launcher_db.json"
JSON_DIR = Path.cwd()

path_variables = [
    STUDIES_IN_DIR,
    FINISHED_DIR,
    LOG_DIR,
]


yaml_file = open(DATA_DIR / "configuration.yaml")
yaml_content = yaml.load(yaml_file, Loader=yaml.FullLoader)
yaml_file.close()
for key, value in yaml_content.items():
    if key in path_variables:
        exec(f"{key} = {Path(value.__repr__())}")
    else:
        exec(f"{key} = {value.__repr__()}")


SSH_CONFIGFILE_PATH_ALTERNATE1 = Path.cwd() / DEFAULT_SSH_CONFIGFILE_NAME
SSH_CONFIGFILE_PATH_ALTERNATE2 = (
    Path.home() / "antares_launcher_settings" / DEFAULT_SSH_CONFIGFILE_NAME
)

# json ssh connection
DEFAULT_SSH_DICT_FROM_EMBEDDED_JSON = None
try:
    with open(DATA_DIR / DEFAULT_SSH_CONFIGFILE_NAME) as ssh_connection_json:
        DEFAULT_SSH_DICT_FROM_EMBEDDED_JSON = json.load(ssh_connection_json)
except IOError:
    print(f"{str(DATA_DIR / DEFAULT_SSH_CONFIGFILE_NAME)} not found")
