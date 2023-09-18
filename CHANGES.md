# Changelog

<!--
This change log can be generated with [`auto-changelog`](https://github.com/CookPete/auto-changelog), for instance :

```shell
npx auto-changelog -l false --hide-empty-releases  -v v1.3.1 -o CHANGES.out.md
``` 
-->

## [1.3.1] - (unreleased)

### Changed

- feat(cli): add the `--solver-version` option to the command line [`#63`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/63)
- feat(parameters): handle the `--partition` and `--qos` parameters for the `sbatch` command [`#58`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/58)

### Fixes

- fix(job-state): consider the `COMPLETING` value as a possible job state [`#61`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/61)
- fix(results-retrieval): handle exceptions in log and ZIP result retrival [`#60`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/60)
- fix(console): use the ISO8601 date format to display messages on the console [`0dbf971`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/0dbf971b1ccc924f4b11cf44b0e0cf16562622c9)

### Refactorings

- refactor: remove IDisplay abstract class [`#64`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/64)

### Chore

- replace `COMPETING` with `COMPLETING` (typo) [`6924a2a`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/6924a2a4ff02c815b44ccb5bc02d0b805bd979cc)

## [1.3.0] - 2023-06-16

### Changed

- Remove "output" exclusion to allow Xpansion sensitivity (now driven by AntaREST) [#46](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/46)
  and [#51](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/5111)

## [1.2.4] - 2023-03-21

### Fixes

- use `scontrol` and `sacct` command to retrieve the job state [#49](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/49) 

## [1.2.3] - 2023-03-16

### Fixes

- Correct download progress bar in logs [#40](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/40)

- Correct SLURM job status checking [#43](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/43)

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

[1.3.1]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.3.1

[1.3.0]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.3.0

[1.2.4]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.2.4

[1.2.3]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.2.3

[1.2.2]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.2.2

[1.2.1]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.2.1

[1.2.0]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.2.0

[1.1.4]: https://github.com/AntaresSimulatorTeam/antares-launcher/releases/tag/v1.1.4
