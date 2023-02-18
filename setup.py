#!/usr/bin/env python

from distutils.core import setup
from antareslauncher import PROJECT_NAME
from antareslauncher import DESCRIPTION
from antareslauncher import VERSION

setup(
    name=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author="RTE, SGATTONI Andrea, MOZGAWA Marc, BION Charly",
    author_email="andrea.sgattoni@rte-france.com",
    url="https://devin-source.rte-france.com/antares/Antares_Launcher.git",
    packages=["antareslauncher"],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Environment :: Console",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": ["Antares_Launcher = antareslauncher.advanced_launch:main"],
    },
)
