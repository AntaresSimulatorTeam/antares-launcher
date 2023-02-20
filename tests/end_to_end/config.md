# End-to-end Configuration for integration tests

## Configuration file templates

The configuration is defined by two file. In this directory, you can find the templates that must be customized
according to your needs:

- The application configuration file: [configuration.yaml](configuration.yaml)
- The SSH configuration file: [ssh_config.json](ssh_config.json) files.

## Default configuration directory

Those files can be stored in the following locations:

- On Windows: `C:\Users\{username}\AppData\Local\RTE`,
- On Mac: `~/Library/Preferences`,
- On Linux: `~/.config` (set by the `XDG_CONFIG_HOME` environment variable).

To run the end-to-end test, you can do:

```shell
cd ~/workspace/antares-launcher
pytest -v --basetemp=target/pytest/ tests/end_to_end/
```

## Custom configuration directory

An alternative is to use a custom location by setting the `ANTARES_LAUNCHER_CONFIG_PATH` environment variable.
This path should point to the `configuration.yaml` file.

In this situation, to run the end-to-end test, you can do:

```shell
export ANTARES_LAUNCHER_CONFIG_PATH=target/config_dir/configuration.yaml
cd ~/workspace/antares-launcher
pytest -v --basetemp=target/pytest/ tests/end_to_end/
```

> **NOTE:** if the configuration file is not found, end-to-end tests are ignored
> and a warning message is printed on the console.
