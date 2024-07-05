# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Common Changelog](https://common-changelog.org/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Changed
- [Issue #233](https://github.com/nasa/ncompare/issues/233): Group dependabot updates into fewer PRs.
### Added
- [Issue #229](https://github.com/nasa/ncompare/issues/229): Added Journal of Open Source Software (JOSS) info to README and CITATION docs.
- [Issue #42](https://github.com/nasa/ncompare/issues/42): Made available via conda and added `conda`/`mamba` installation instructions to README.md
### Removed
- [Issue #231](https://github.com/nasa/ncompare/issues/231): Removed upper bounds from dependencies
### Fixed
- [Pull #230](https://github.com/nasa/ncompare/pull/230): Fixed help text for second NetCDF file passed on command line


## [1.9.0] - 2024-05-29

### Changed
- [Issue #184](https://github.com/nasa/ncompare/issues/184): Change license to Apache License 2.0. and include copyright header text
- [Issue #200](https://github.com/nasa/ncompare/issues/200): Change dependabot frequency to monthly
### Added
- [Issue #210](https://github.com/nasa/ncompare/issues/210): Add gif of usage to readme
### Fixed
- [Issue #208](https://github.com/nasa/ncompare/issues/208): Fix missing group error
- [Pull #190](https://github.com/nasa/ncompare/pull/190): Fix codecov upload token error
- [Pull #199](https://github.com/nasa/ncompare/pull/199): Resolve linting error


## [1.8.0] - 2024-03-12

### Changed
- update dependencies
- update citation
- [pull/168](https://github.com/nasa/ncompare/pull/168): updated syntax for new linting checks


## [1.7.3] - 2024-02-06

### Changed
- add Zenodo badge to readme


## [1.7.2] - 2024-02-06

### Changed
- add pyOpenSci badge to readme


## [1.7.1] - 2024-02-06

### Changed
- update dependencies
- update citation


## [1.7.0] - 2024-02-06

### Changed
- [pull/136](https://github.com/nasa/ncompare/pull/136): Replace data in example notebook with those requiring no credentials
### Fixed
- [pull/135](https://github.com/nasa/ncompare/pull/135): Fix links in readme


## [1.6.2] - 2024-01-16

### Changed

- updated PyPI classifiers in pyproject.toml


## [1.6.1] - 2024-01-16

### Changed
- [pull-request/125](https://github.com/nasa/ncompare/pull/125): Bump jinja2 from 3.1.2 to 3.1.3
### Removed
- removed unused placeholder file and .images folder


## [1.6.0] - 2024-01-16

### Changed
- [pull-request/99](https://github.com/nasa/ncompare/pull/99): Improve readme in a few ways (e.g., license, badges)
- [pull-request/106](https://github.com/nasa/ncompare/pull/106): Use ReadTheDocs instead of GitHub Pages for documentation
- [pull-request/113](https://github.com/nasa/ncompare/pull/113): Add codecov step to tests workflow
- [issue/88](https://github.com/nasa/ncompare/issues/88): Improve test coverage, especially for ncompare/core.py and ncompare/printing.py
- [issue/92](https://github.com/nasa/ncompare/issues/92): Ensure examples utilize publicly accessible data
- [pull-request/121](https://github.com/nasa/ncompare/pull/121): Disable text wrapping to properly show ncompare output in notebook example
- Tweaked wording regarding docstrings in the contributing guide
### Added
- [pull-request/79](https://github.com/nasa/ncompare/pull/79): Add option to only display variables and attributes that are different
- [pull-request/100](https://github.com/nasa/ncompare/pull/100): Add version to cli
- [pull-request/105](https://github.com/nasa/ncompare/pull/105): Add testing of ncompare with Python version 3.12
- [issue/118](https://github.com/nasa/ncompare/issues/118): Add citation file
### Removed
- Fixed bug related to extra argument from command line
### Fixed
- Updated out-dated example snippet in README


## [1.5.0] - 2023-10-25
### Added
- [pull-request/63](https://github.com/nasa/ncompare/pull/59): Add a tutorial example notebook.
- Added a simple GitHub Pages that links to an quarto-produced version of the tutorial notebook.


## [1.4.0] - 2023-10-23

### Added
- [pull-request/59](https://github.com/nasa/ncompare/pull/59): Add the ability to modify the width of each column in the comparison table.
### Fixed
- [pull-request/60](https://github.com/nasa/ncompare/pull/60): Removes an extra line of printed filepaths.


## [1.3.0] - 2023-10-20

### Fixed
- [pull-request/55](https://github.com/nasa/ncompare/pull/55): Fix variable value matching


## [1.2.0] - 2023-10-11

### Changed
- [pull-request/47](https://github.com/nasa/ncompare/pull/47): Added coverage and move test running to separate workflow yml
### Added
- [pull-request/44](https://github.com/nasa/ncompare/pull/44): Added issue templates and markdown guides for CONTRIBUTING and the CODE_OF_CONDUCT


## [1.1.0] - 2023-09-26

### Changed
- [pull-request/28](https://github.com/nasa/ncompare/pull/28): Updated CI/CD versions, and updated README.md
### Added
- [commit/4b98808](https://github.com/nasa/ncompare/commit/4b98808cf3d8424da25a226687d304ce7d46738e): Set up dependabot for automated version updates


## [1.0.2] - 2023-09-20

### Changed
- Use ruff and black for linting and formatting [issue/23](https://github.com/nasa/ncompare/issues/23)
### Added
- Add automated publishing (via poetry) to TestPyPI and PyPI in Actions workflow [issue/19](https://github.com/nasa/ncompare/issues/19)


## [1.0.1] - 2023-09-06

### Changed
- Improve test suite [#12](https://github.com/nasa/ncompare/issues/12):
- Enable `ncompare` to work with greater group depths [#13](https://github.com/nasa/ncompare/issues/13):
### Added
### Removed
### Fixed
- Fix author attribute for poetry [#5](https://github.com/nasa/ncompare/issues/5)
