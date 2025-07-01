# Changelog

<!--
This change log can be generated with [`auto-changelog`](https://github.com/CookPete/auto-changelog), for instance :

```shell
npx auto-changelog -l false --hide-empty-releases  -v v1.3.1 -o CHANGES.out.md
``` 
-->

## [1.4.4] - 2025-07-01

### Changed

- ci: test with python v3.11 [#81](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/81)
- fix(ci): use ubuntu 22 workers instead of 20 [#86](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/86)
- fix(download): retrieve output directory on error [#85](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/85)
- feat(command_line): give all `other_options` inside quotes to slurm [#84](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/84)

## [1.4.3] - 2024-10-10

### Changed

- build(binaries): build binaries on release [`#78`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/78)

### Breaking change

- feat(version): use `antares-study-version` package to handle versions [`#79`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/79)
  :warning: the sbatch command is now "8.8" instead of "880" when giving the study version. So you'll have to change your .sh file.

## [1.4.2] - 2024-09-17

### Changed

- build(deps): bump paramiko version [`#73`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/73)
- fix(workflows): bump gh actions + use os names to build binaries to avoid conflicts, [`#74`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/74) and [`#75`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/75)


## [1.4.1] - 2024-04-11

### Fixes

- fix(retriever): avoid infinite loop if sbatch command fails [`#69`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/69)


## [1.4.0] - 2023-12-19

### Changed

- feat(ssh): add retry loop around SSH Exceptions [`#68`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/68)
- feat(zip-extractor): add support for -z option [`#67`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/67)


## [1.3.2] - 2024-04-11

### Build

- build: add a script to bump the version

### Changed

- feat(ssh): add retry loop around SSH Exceptions [`#68`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/68)

### Fixes

- fix(retriever): avoid infinite loop if sbatch command fails [`#69`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/69)


## [1.3.1] - 2023-09-26

### Changed

- feat(database): simplify launcher database implementation [`#66`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/66)
- feat(cli): add the `--solver-version` option to the command line [`#63`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/63)
- feat(parameters): handle the `--partition` and `--qos` parameters for the `sbatch` command [`#58`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/58)
- feat(retrival): correct the retrival of remote files and improve exception handling to avoid infinite loops [`88efc98`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/88efc98af6a8fd494f07cc9a366a52109eb3ac2d)
- feat(zip-extractor): the uncompress directory is calculated according to the content: study directory or simulation output [`1ffc86e`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/1ffc86e0439814e4549f59c193731c71080c0d59)

### Fixes

- fix(cli): preserve backward compatibility in CLI options [`#65`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/65)
- fix(job-state): consider the `COMPLETING` value as a possible job state [`#61`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/61)
- fix(results-retrieval): handle exceptions in log and ZIP result retrival [`#60`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/60)
- fix(console): use the ISO8601 date format to display messages on the console [`0dbf971`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/0dbf971b1ccc924f4b11cf44b0e0cf16562622c9)

### Refactorings

- refactor: remove `IDisplay` abstract class [`#64`](https://github.com/AntaresSimulatorTeam/antares-launcher/pull/64)
- refactor(launch-controller): simplification of the `LaunchController` class [`4c07551`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/4c07551ae8acf15d784553e7877b9017626b306b)
- refactor(file-manager): remove unused or trivial methods from `FileManager` [`fbb60e0`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/fbb60e0efca6989e7ea79324ed746b55da3cfb3d)
- refactoring(file-manager): drop the `FileManager` class [`9797799`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/9797799df6bf4fd626ea1bc997d11503989d5b94)
- refactoring(tree-structure): drop the `TreeStructureInitializer` class [`8a119af`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/8a119afb06d64f0ccd1e112ef82367f8fdee7ce0)
- refactoring(data-provider): drop the `DataProvider` class [`272965e`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/272965ed618f94ecf0de718bf7e8e0788c4bbb3a)

### Code Style

- style: reformat source code using iSort and Black [`e243fba`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/e243fbab177c46ffc867440b3701d7672566066c)

### Chore

- chore(typing): improve the typing of study parameters [`f11641d`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/f11641d4d233d61f91b9cbebf6263780ff14eb88)
- chore(typing): improve typing in source code [`4ff6abf`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/4ff6abf512b03944d0132d868484ef2d677c8b77)
- chore: replace `COMPETING` with `COMPLETING` (typo) [`e98b7a8`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/e98b7a8627b09a883e48a9b4b883f6b1560da0e9)

### Tests

- test: correct the test fixtures for study retrival [`6f78bd6`](https://github.com/AntaresSimulatorTeam/antares-launcher/commit/6f78bd62a5f7c6b61a6fcb4a9a42c7710e986301)


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
