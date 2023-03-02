# Changelog

## [1.2.2] - 2023-03-02

### Fixes

- Preserve the log files if the study processing is not
  finished [#37](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/37)

## [1.2.1] - 2023-02-24

### Fixes

- Correct install_requires to be compatible with AntaREST project

## [1.2.0] - 2023-02-21

### Added

- Add a deployment GitHub action to build Antares_Launcher
  executable [#22](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/22)
- Prepare python library [#18](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/18)
- Describe the application configuration file parameters

### Fixes

- Ensure ZIP and log files are removed after
  download [#20](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/20)

### Refactorings

- Introduce parameters reader.py [#9](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/9)
- Rename a few variables and parameters
- Remove end-to-end tests
- Change the build name

### Docs

- Update and improve the documentation [#24](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/24)

## [1.1.4] - 2021-05-25

### Added

- Partial feature: study list composer
- Add remove_study function
- Add show_banner option

### Refactorings

- Rename alternate path for ssh configfile
- Change default value for show_banner of main.run_with
- Black + optional ssh config file

### Fixes

- Fix main_option_parser test
- Fix gitignore
- Fix listo composer

### Miscellaneous

- Remove definitions from unit and integration tests
- Remove definitions from data repo tinydb
- Remove definitions from main.py
- Remove definitions from main options parser
- Remove definitions from slurm_script_features
- Remove definitions from study list composer
- Apply black
- Update LICENCE
- Initial commit
- First release (251ed9b
- Add proper output for `study_list_composer.py`
- Remove unnecessary Optional
- Enable ssh_config_file to be `None`

[1.2.2]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.2.2

[1.2.1]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.2.1

[1.2.0]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.2.0

[1.1.4]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.1.4
