"""
Antares Launcher

This program is meant to allow the user to send a list of Antares simulations
on a remote Linux machine that can run them using *SLURM Workload Manager*.

This module contains the project metadata.
"""

# Standard project metadata

__version__ = "1.2.2"
__author__ = "RTE, Antares Web Team"
__date__ = "2023-03-02"
# noinspection SpellCheckingInspection
__credits__ = "(c) Réseau de Transport de l’Électricité (RTE)"

# Extra project metadata
__project_name__ = "Antares_Launcher"


def _check_metadata():
    # noinspection SpellCheckingInspection
    """
    Check the project metadata.

    To update the project metadata, you can run the following command:
    ```shell
    python setup.py egg_info
    ```

    To get the list of tags and release dates, you can also run:
    ```shell
    git for-each-ref --sort=-creatordate --format '%(refname:strip=2) (%(creatordate:short))' refs/tags
    ```
    """
    from pkg_resources import get_distribution

    dist = get_distribution(__project_name__)
    # Expected distribution name should be "antares-launcher":
    dist_name = __project_name__.lower().replace("_", "-")
    assert dist.key == dist_name, dist.key
    assert dist.version == __version__, dist.version
    print("Project metadata OK.")


if __name__ == "__main__":
    # run the shell command `python antareslauncher/__init__.py ` to check
    _check_metadata()
