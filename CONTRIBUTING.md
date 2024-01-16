# Contributing to _ncompare_

Thank you for contributing to _ncompare_!

### Table of Contents

- [How to Contribute](CONTRIBUTING.md#how-to-contribute)
    - [Reporting Bugs](CONTRIBUTING.md#reporting-bugs)
    - [Feature Requests](CONTRIBUTING.md#featureenhancement-requests)
    - [Pull Requests](CONTRIBUTING.md#pull-requests)
    - [Branches](CONTRIBUTING.md#branches)
    - [Changelog](CONTRIBUTING.md#changelog)
    - [Testing](CONTRIBUTING.md#testing)
    - [Reviewing](CONTRIBUTING.md#reviewing)
- [Style Guides](CONTRIBUTING.md#style-guides)
    - [Python Style Guide](CONTRIBUTING.md#python-style-guide)
    - [Documentation Style Guide](CONTRIBUTING.md#documentation-1)


## How to Contribute

### Reporting Bugs

Bugs can be reported by creating a new GitHub issue in this repository.
Please use the `bug` label on any bug issue created. Provide detailed
instructions on how to reproduce the bug if possible. Include the version
of _ncompare_ that produced this bug and specific error messages.

### Feature/Enhancement Requests

Feature/enhancement requests are tracked with GitHub issues. Please use
an appropriate label:

- `documentation`
    - Docstring or documentation changes
- `automation`
    - Anything related to CI/CD or metadata
- `enhancement`
    - Improvement of an existing feature
- `new-feature`
    - An entirely new feature

Feature and enhancement requests should contain a detailed description
of the desired behavior and rationale.

### Pull Requests

Please ensure all pull requests follow the PR
[template](/.github/pull_request_template.md). This is to ensure

* A reviewer understands what is being changed
* A reviewer understands why it is being changed
* A reviewer understands how the changes have been verified
* A reviewer is confident the changes work as expected and won't break existing functionality.

The name of the pull request should be meaningful, and if the pull
request is addressing a GitHub issue, should match the name of the
GitHub issue.

If any performance improvements are being made, please include graphs or charts.

### Branches

- `develop` (protected)
    - Code actively being developed
- `main` (protected)
    - Matches the version currently in prod
- `release/#.#.#`
    - Release branch being considered for delivery to prod.
    - Matches the version currently in test
- `feature/issue-#`
    - Work for enhancements and new features should be done in a branch with this naming convention
    - The issue number should match the associated GitHub issue number
- `bugfix/issue-#`
    - Work for bug fixes should be done in a branch with this naming convention
    - The issue number should match the associated GitHub issue number
- `hotfix/issue-#` or `hotfix/short-fix-description`
    - Rare/special case to address a special anomaly.
    - The issue number should match the associated GitHub issue number,
    unless no such issue exists. If not, use a short description of the
    issue e.g. `hotfix/fix-request-url`

### Changelog

_Ncompare_ maintains a [changelog](CHANGELOG.md). See
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) for more
information.

The top of the changelog will contain an `[Unreleased]` section. Add
any changes made in the current PR to the appropriate section of the
changelog.

Please keep changelog messages relatively short (1-2 sentences).

### Testing

In most cases, unit tests should be either created or updated in every PR.

Most Python modules are accompanied by an associated test file named
`test_nameofmodule.py`. If resources are needed for unit tests, they
should be placed in `tests/data`. Test coverage reports are generated
as part of the CI/CD pipeline.


### Reviewing

Another valuable way to contribute to the project is to review pull
requests. Pull requests reviews are appreciated and valued by anybody
at any skill level.

#### Review responsibilities

This list is intended for people conducting code reviews of pull
requests. When reviewing a pull request, the reviewer should use the
following checklist to verify that the code will not break clients or
cause problems; that the code/tests are correct, complete, follow
conventions/guidelines, and can be merged into the `main` branch without
issue. Some items on the list are very specific, e.g., no TODOs,
while others are more open-ended (well-structured tests). The list is
intended to make the job of reviewing pull requests easier and more
repeatable by identifying areas in pull requests that commonly need
addressing.

When reviewing a pull request, start at the top of the list and consider
the most important things that could lead to problems. These are
outlined as a set of questions in the Most Important section. Check off
the boxes when you are satisfied that each of the criteria is met. Then
proceed to the more specific items below in the General, Testing, and
Documentation sections.  Check off each box that is satisfied by the
pull request and add comments to the pull request for those that are
not. If all the boxes are checked, then approve the request. Otherwise,
mark it as needing work, or, if there are critical errors, decline it.

#### Most Important (Primum non nocere—"First, do no harm")

- Could this change break clients?
- Do the changes handle data that may have been previously saved or
indexed by an older version of the code?
- What is the operational impact of this change—are there any
potential issues such as special deployment procedures, performance
issues, etc.?
- Are there tests for all cases (including edge cases)?
- What could go wrong?

#### General
- Does the code do what it's supposed to do?
- Have they implemented all the acceptance criteria?
- There are no overly long or complicated functions that should be
broken up for readability
- Are web API parameters validated?
- Are symbols used rather than “magic number” constants or string
constants? (OK in tests, particularly for error messages or response codes)
- There is no repeated or copy-and-paste code / tests
- There are no TODOs
- There are no stray comment blocks, commented out code, capture/reveals,
proto-saves, printlns, or unnecessary logging
- All namespaces and non-trivial defs/defns/defmacros have docstrings
- There are no dangling _requires_, i.e., requires that were added and
not used or requires that are no longer necessary due to code removal
- Code conventions are followed

#### Testing
- If the issue is a bug fix - a test was added that reproduces the
conditions that triggered the bug
- The tests are well-structured and follow current practices

#### Documentation
- Documentation (api_docs.md, README.md, etc.) was added for any new
features or old documentation updated for any changed features
- Code/curl examples or sample data have been updated as necessary
- Has the CHANGELOG been updated?

## Style Guides

### Python Style Guide

_Ncompare_ follows PEP8 as much as possible. Reference the _ruff_ and
_black_ configuration sections in [pyproject.toml](pyproject.toml) for specific expectations.

### Documentation

_Ncompare_ uses [Numpy docstrings](https://numpydoc.readthedocs.io/en/latest/format.html).
All functions should contain a docstring, though private functions (that are exceptionally short)
may contain a 1-line docstring.
