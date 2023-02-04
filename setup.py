#!/usr/bin/env python
import pathlib

from setuptools import setup, find_packages

from antareslauncher import __author__, __project_name__, __version__

# Dependencies required to install the application in "production" or "development" mode.
# Use `pip install -e .` to install in "development" mode.
# The version numbers are loosely constrained to allow installation of bugfix versions,
# but sufficiently constrained to avoid incompatibilities.
# It is the developer's responsibility to update versions: unit tests should
# detect incompatibility problems.
# Warning: this package is used as a library, so you should not constrain the versions too much.
install_requires = [
    "paramiko < 3.0",  # version 3.0.0 is not mature yet (2023-01-22)
    "PyYAML < 6.1",
    "tinydb < 4.8",
    "tqdm < 4.65",
]

# Dependencies used for testing in "development" mode.
# Use `pip install -e .[test]` to install.
test_requires = [
    "pytest ~= 7.2.1",
    "pytest-cov ~= 4.0.0",
    "pytest-xdist ~= 3.1.0",
]

setup(
    name=__project_name__,
    version=__version__,
    description="Antares_Launcher to run Antares on a remote linux machine",
    long_description=pathlib.Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author=__author__,
    author_email="andrea.sgattoni@rte-france.com",
    url="https://devin-source.rte-france.com/antares/Antares_Launcher.git",
    packages=find_packages(exclude=["tests*"]),
    install_requires=install_requires,
    extras_require={
        "test": test_requires,
    },
    license="Apache Software License",
    platforms=[
        "linux-x86_64",
        "macosx-10.14-x86_64",
        "macosx-10.15-x86_64",
        "macosx-11-x86_64",
        "macosx-12-x86_64",
        "macosx-13-x86_64",
        "win-amd64",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    entry_points={
        "console_scripts": ["Antares_Launcher = antareslauncher.advanced_launch:main"],
    },
    python_requires=">=3.8, <4",
)
