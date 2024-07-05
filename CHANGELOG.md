# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Common Changelog](https://common-changelog.org/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Changed

- Group dependabot updates into fewer PRs ([#233](https://github.com/nasa/ncompare/issues/233)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Add Journal of Open Source Software (JOSS) info to README and CITATION docs ([#229](https://github.com/nasa/ncompare/issues/229)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Make available via conda and add `conda`/`mamba` installation instructions to README.md ([#42](https://github.com/nasa/ncompare/issues/42)) ([**@jhkennedy**](https://github.com/jhkennedy), [**@danielfromearth**](https://github.com/danielfromearth))

### Removed

- Remove upper bounds from dependencies ([#231](https://github.com/nasa/ncompare/issues/231)) ([**@jhkennedy**](https://github.com/jhkennedy), [**@danielfromearth**](https://github.com/danielfromearth))

### Fixed

- Fix help text for second NetCDF file passed on command line ([#230](https://github.com/nasa/ncompare/pull/230)) ([**@berquist**](https://github.com/berquist))


## [1.9.0] - 2024-05-29

### Changed

- Change license to Apache License 2.0. and include copyright header text ([#184](https://github.com/nasa/ncompare/issues/184)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Change dependabot frequency to monthly ([#200](https://github.com/nasa/ncompare/issues/200)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Add gif of usage to readme ([#210](https://github.com/nasa/ncompare/issues/210)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Fixed
- Fix missing group error ([#208](https://github.com/nasa/ncompare/issues/208)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Fix codecov upload token error ([#190](https://github.com/nasa/ncompare/pull/190)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Resolve linting error ([#199](https://github.com/nasa/ncompare/pull/199)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.8.0] - 2024-03-12

### Changed

- Update dependencies ([#169](https://github.com/nasa/ncompare/pull/169)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Update citation ([`2178b97`](https://github.com/nasa/ncompare/pull/169/commits/2178b970fa32fa820c03d9c8c82b0ef8d8249150)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Update syntax for new linting checks ([#168](https://github.com/nasa/ncompare/pull/168)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.7.3] - 2024-02-06

### Changed

- Add Zenodo badge to readme ([#149](https://github.com/nasa/ncompare/pull/149)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.7.2] - 2024-02-06

### Changed

- Add pyOpenSci badge to readme ([#148](https://github.com/nasa/ncompare/pull/148)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.7.1] - 2024-02-06

### Changed

- Update dependencies ([#147](https://github.com/nasa/ncompare/pull/147)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Update citation ([#147](https://github.com/nasa/ncompare/pull/147)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.7.0] - 2024-02-06

### Changed

- Replace data in example notebook with those requiring no credentials ([#136](https://github.com/nasa/ncompare/pull/136)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Fixed

- Fix links in readme ([#135](https://github.com/nasa/ncompare/pull/135)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.6.2] - 2024-01-16

### Changed

- Update PyPI classifiers in pyproject.toml ([#130](https://github.com/nasa/ncompare/pull/130)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.6.1] - 2024-01-16

### Changed

- Bump jinja2 from 3.1.2 to 3.1.3 ([#125](https://github.com/nasa/ncompare/pull/125)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Removed

- Remove unused placeholder file and .images folder ([#128](https://github.com/nasa/ncompare/pull/128)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.6.0] - 2024-01-16

### Changed

- Improve readme in a few ways (e.g., license, badges) ([#99](https://github.com/nasa/ncompare/pull/99)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Use ReadTheDocs instead of GitHub Pages for documentation ([#106](https://github.com/nasa/ncompare/pull/106)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Add codecov step to tests workflow ([#113](https://github.com/nasa/ncompare/pull/113)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Improve test coverage, especially for ncompare/core.py and ncompare/printing.py ([#88](https://github.com/nasa/ncompare/issues/88)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Ensure examples utilize publicly accessible data ([#92](https://github.com/nasa/ncompare/issues/92)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Disable text wrapping to properly show ncompare output in notebook example ([#121](https://github.com/nasa/ncompare/pull/121)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Tweak wording regarding docstrings in the contributing guide ([`9c20671`](https://github.com/nasa/ncompare/pull/124/commits/9c2067147036947e47daafaf6b31a08821a1417b)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Add option to only display variables and attributes that are different ([#79](https://github.com/nasa/ncompare/pull/79)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Add version to cli ([#100](https://github.com/nasa/ncompare/pull/100)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Add testing of ncompare with Python version 3.12 ([#105](https://github.com/nasa/ncompare/pull/105)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Add citation file ([#118](https://github.com/nasa/ncompare/issues/118)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Removed

- Fix bug related to extra argument from command line ([#124](https://github.com/nasa/ncompare/pull/124)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Fixed

- Update out-dated example snippet in README ([`eaddcad`](https://github.com/nasa/ncompare/pull/124/commits/eaddcad999ac52a06fdd95b7a8874bad4785111d)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.5.0] - 2023-10-25

### Added

- Add a tutorial example notebook ([#63](https://github.com/nasa/ncompare/pull/63)) ([**@danielfromearth**](https://github.com/danielfromearth))
- Add a simple GitHub Pages that links to an quarto-produced version of the tutorial notebook. ([#64](https://github.com/nasa/ncompare/pull/64)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.4.0] - 2023-10-23

### Added

- Add the ability to modify the width of each column in the comparison table ([#59](https://github.com/nasa/ncompare/pull/59)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Fixed

- Remove an extra line of printed filepaths ([#60](https://github.com/nasa/ncompare/pull/60)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.3.0] - 2023-10-20

### Fixed

- Fix variable value matching ([#55](https://github.com/nasa/ncompare/pull/55)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.2.0] - 2023-10-11

### Changed

- Add coverage and move test running to separate workflow yml ([#47](https://github.com/nasa/ncompare/pull/47)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Add issue templates and markdown guides for CONTRIBUTING and the CODE_OF_CONDUCT ([#44](https://github.com/nasa/ncompare/pull/44)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.1.0] - 2023-09-26

### Changed

- Update CI/CD versions, and updated README.md ([#28](https://github.com/nasa/ncompare/pull/28)) ([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Set up dependabot for automated version updates ([`4b98808`](https://github.com/nasa/ncompare/commit/4b98808cf3d8424da25a226687d304ce7d46738e)) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.0.2] - 2023-09-20

### Changed

- Use ruff and black for linting and formatting [#23](https://github.com/nasa/ncompare/issues/23) ([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Add automated publishing (via poetry) to TestPyPI and PyPI in Actions workflow [#19](https://github.com/nasa/ncompare/issues/19) ([**@danielfromearth**](https://github.com/danielfromearth))


## [1.0.1] - 2023-09-06

### Changed

- Improve test suite [#12](https://github.com/nasa/ncompare/issues/12) ([**@danielfromearth**](https://github.com/danielfromearth))
- Enable `ncompare` to work with greater group depths [#13](https://github.com/nasa/ncompare/issues/13) ([**@danielfromearth**](https://github.com/danielfromearth))

### Fixed

- Fix author attribute for poetry [#5](https://github.com/nasa/ncompare/issues/5) ([**@danielfromearth**](https://github.com/danielfromearth))
