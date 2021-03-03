# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
 - clicking a date entry label in the 'Project info' view will clear its contents
 - report export as CSV (default)
 - report export as JSON 
### Changed
 - rinse windows will be titled after the system they control
 - requests for rinse cycles will be ignored if a test is already running
 - the Live Plot stops updating (clearing itself) at the end of a test
 - evaluation windows will title themselves after their test handler and project
 - minor performance improvement to evaluation window
### Fixed
 - observed baseline pressure reporting
### Removed
 - dependency on openpyxl
 - dependency on PIL
 - ability to export report as .xlsx
 - redundant tabs from EvaluationFrame

## [v0.1.0]
### Added
 - rinse dialog, accessible from the menu bar
 - help text, accessible from the menu bar
 - get_resource function for getting resource files. can be used for resources with bundled executables later 
### Changed 
 - reset versioning to 0.1.0
 - moved project loading functionality to menu bar

[Unreleased]: https://github.com/teauxfu/pct-scalewiz
[v0.1.0]: https://github.com/teauxfu/pct-scalewiz/releases/tag/v0.1.0