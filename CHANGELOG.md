# Changelog

## v2.2.1 (2025-07-08)

### Fix

- test truthyness of package.owner_org
- don't just test owner_org for null
- accept org admins and editors as members

### Tests

- fix tests to allow editors and admins

## v2.2.0 (2025-06-09)

### Feature

- add auth functions for managing collaborators

### Refactor

- load actions and auth with ckantools

### Tests

- add tests for collaborator management auth functions

### CI System(s)

- set ruff target py version, add more ignores - avoid using fixes that don't work for python 3.8 (our current version) - ignore recommended ruff formatter conflicts - ignore more docstring rules
- remove pylint, add ruff lint rules Primarily the defaults plus pydocstyle and isort.
- update pre-commit repo versions

## v2.1.11 (2025-05-27)

### Fix

- get package id from deferred auth
- remove package member default auth

### Tests

- add test for collaborator permissions override
- fix tests after org member permissions change

## v2.1.10 (2024-11-04)

### Docs

- use variable logo based on colour scheme
- fix tests badge tests workflow file was renamed

### Style

- automatic reformat auto reformat with ruff/docformatter/prettier after config changes

### Build System(s)

- remove version from docker compose file version specifier is deprecated

### CI System(s)

- fix python setup action version
- add merge to valid commit types
- add docformatter args and dependency docformatter currently can't read from pyproject.toml without tomli
- only apply auto-fixes in pre-commit F401 returns linting errors as well as auto-fixes, so this disables the errors and just applies the fixes
- update tool config update pre-commit repo versions and switch black to ruff
- add pull request validation workflow new workflow to check commit format and code style against pre-commit config
- update workflow files standardise format, change name of tests file

### Chores/Misc

- add pull request template
- update tool details in contributing guide

## v2.1.9 (2024-08-20)

### Chores/Misc

- add build section to read the docs config
- add regex for version line in citation file
- add citation.cff to list of files with version
- add contributing guidelines
- add code of conduct
- add citation file
- update support.md links

## v2.1.8 (2023-07-17)

### Docs

- update logos

## v2.1.7 (2023-04-11)

### Build System(s)

- fix postgres not loading when running tests in docker

### Chores/Misc

- add action to sync branches when commits are pushed to main

## v2.1.6 (2023-02-20)

### Docs

- fix api docs generation script

### Chores/Misc

- small fixes to align with other extensions

## v2.1.5 (2023-01-31)

### Docs

- **readme**: change logo url from blob to raw

## v2.1.4 (2023-01-31)

### Docs

- **readme**: direct link to logo in readme
- **readme**: fix github actions badge

## v2.1.3 (2023-01-30)

### Build System(s)

- **docker**: use 'latest' tag for test docker image

## v2.1.2 (2022-12-12)

### Style

- change quotes in setup.py to single quotes

### Build System(s)

- include top-level data files in theme folder
- add package data

## v2.1.1 (2022-12-01)

### Docs

- **readme**: format test section
- **readme**: update installation steps
- **readme**: update ckan patch version in header badge

## v2.1.0 (2022-11-28)

### Docs

- add section delimiters and include-markdown

### Style

- apply formatting

### Build System(s)

- set changelog generation to incremental
- pin ckantools minor version

### CI System(s)

- add cz-nhm dependency

### Chores/Misc

- use cz_nhm commitizen config
- standardise package files

## v2.0.0 (2021-03-09)

## v1.0.0-alpha (2019-07-23)

## v0.0.1 (2016-12-12)

## ckanext-userdatasets-0.1 (2014-06-13)
