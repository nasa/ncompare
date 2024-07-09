# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- [Issue #246](https://github.com/nasa/ncompare/issues/246): Changed xarray Dataset.dims reference to Dataset.sizes due to FutureWarning

## [1.9.0]
### Added
- [Issue #210](https://github.com/nasa/ncompare/issues/210): Add gif of usage to readme
### Changed
- [Issue #184](https://github.com/nasa/ncompare/issues/184): Change license to Apache License 2.0. and include copyright header text
- [Issue #200](https://github.com/nasa/ncompare/issues/200): Change dependabot frequency to monthly
### Deprecated
### Removed
### Fixed
- [Issue #208](https://github.com/nasa/ncompare/issues/208): Fix missing group error
- [Pull #190](https://github.com/nasa/ncompare/pull/190): Fix codecov upload token error
- [Pull #199](https://github.com/nasa/ncompare/pull/199): Resolve linting error
### Security

## [1.8.0] - 2024-03-12
### Added
### Changed
- update dependencies
- update citation
- [pull/168](https://github.com/nasa/ncompare/pull/168): updated syntax for new linting checks
### Deprecated
### Removed
### Fixed
### Security

## [1.7.3] - 2024-02-06
### Added
### Changed
- add Zenodo badge to readme
### Deprecated
### Removed
### Fixed
### Security

## [1.7.2] - 2024-02-06
### Added
### Changed
- add pyOpenSci badge to readme
### Deprecated
### Removed
### Fixed
### Security

## [1.7.1] - 2024-02-06
### Added
### Changed
- update dependencies
- update citation
### Deprecated
### Removed
### Fixed
### Security

## [1.7.0] - 2024-02-06
### Added
### Changed
- [pull/136](https://github.com/nasa/ncompare/pull/136): Replace data in example notebook with those requiring no credentials
### Deprecated
### Removed
### Fixed
- [pull/135](https://github.com/nasa/ncompare/pull/135): Fix links in readme
### Security

## [1.6.2] - 2024-01-16
### Added
### Changed
- updated PyPI classifiers in pyproject.toml
### Deprecated
### Removed
### Fixed
### Security

## [1.6.1] - 2024-01-16
### Added
### Changed
### Deprecated
### Removed
- removed unused placeholder file and .images folder
### Fixed
### Security
- [pull-request/125](https://github.com/nasa/ncompare/pull/125): Bump jinja2 from 3.1.2 to 3.1.3

## [1.6.0] - 2024-01-16
### Added
- [pull-request/79](https://github.com/nasa/ncompare/pull/79): Add option to only display variables and attributes that are different
- [pull-request/100](https://github.com/nasa/ncompare/pull/100): Add version to cli
- [pull-request/105](https://github.com/nasa/ncompare/pull/105): Add testing of ncompare with Python version 3.12
- [issue/118](https://github.com/nasa/ncompare/issues/118): Add citation file
### Changed
- [pull-request/99](https://github.com/nasa/ncompare/pull/99): Improve readme in a few ways (e.g., license, badges)
- [pull-request/106](https://github.com/nasa/ncompare/pull/106): Use ReadTheDocs instead of GitHub Pages for documentation
- [pull-request/113](https://github.com/nasa/ncompare/pull/113): Add codecov step to tests workflow
- [issue/88](https://github.com/nasa/ncompare/issues/88): Improve test coverage, especially for ncompare/core.py and ncompare/printing.py
- [issue/92](https://github.com/nasa/ncompare/issues/92): Ensure examples utilize publicly accessible data
- [pull-request/121](https://github.com/nasa/ncompare/pull/121): Disable text wrapping to properly show ncompare output in notebook example
- Tweaked wording regarding docstrings in the contributing guide
### Deprecated
### Removed
- Fixed bug related to extra argument from command line
### Fixed
- Updated out-dated example snippet in README
### Security

## [1.5.0] - 2023-10-25
### Added
- [pull-request/63](https://github.com/nasa/ncompare/pull/59): Add a tutorial example notebook.
- Added a simple GitHub Pages that links to an quarto-produced version of the tutorial notebook.
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [1.4.0] - 2023-10-23
### Added
- [pull-request/59](https://github.com/nasa/ncompare/pull/59): Add the ability to modify the width of each column in the comparison table.
### Changed
### Deprecated
### Removed
### Fixed
- [pull-request/60](https://github.com/nasa/ncompare/pull/60): Removes an extra line of printed filepaths.
### Security

## [1.3.0] - 2023-10-20
### Added
### Changed
### Deprecated
### Removed
### Fixed
- [pull-request/55](https://github.com/nasa/ncompare/pull/55): Fix variable value matching
### Security

## [1.2.0] - 2023-10-11
### Added
- [pull-request/44](https://github.com/nasa/ncompare/pull/44): Added issue templates and markdown guides for CONTRIBUTING and the CODE_OF_CONDUCT
### Changed
- [pull-request/47](https://github.com/nasa/ncompare/pull/47): Added coverage and move test running to separate workflow yml
### Deprecated
### Removed
### Fixed
### Security

## [1.1.0] - 2023-09-26
### Added
- [commit/4b98808](https://github.com/nasa/ncompare/commit/4b98808cf3d8424da25a226687d304ce7d46738e): Set up dependabot for automated version updates
### Changed
- [pull-request/28](https://github.com/nasa/ncompare/pull/28): Updated CI/CD versions, and updated README.md
### Deprecated
### Removed
### Fixed
### Security

## [1.0.2] - 2023-09-20
### Added
- Add automated publishing (via poetry) to TestPyPI and PyPI in Actions workflow [issue/19](https://github.com/nasa/ncompare/issues/19)
### Changed
- Use ruff and black for linting and formatting [issue/23](https://github.com/nasa/ncompare/issues/23)
### Deprecated
### Removed
### Fixed
### Security

## [1.0.1] - 2023-09-06
### Added
### Changed
- Improve test suite [#12](https://github.com/nasa/ncompare/issues/12):
- Enable `ncompare` to work with greater group depths [#13](https://github.com/nasa/ncompare/issues/13):
### Deprecated
### Removed
### Fixed
- Fix author attribute for poetry [#5](https://github.com/nasa/ncompare/issues/5)
### Security
