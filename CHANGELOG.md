# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
 - clicking a date entry label in the 'Project info' view will clear its contents
 - report export as CSV (default)
 - report export as flattened JSON (not human readable)
 - more descriptive window titles, all windows get the app icon
### Changed
 - performance improvement to evaluation window
 - time resolution improvement to data collection loop
 - rinse windows will be titled after the system they control
 - requests for rinse cycles will be ignored if a test is already running
 - the Live Plot scales the limits of its axes to the data collected
 - evaluation windows will title themselves after their test handler and project
 - refactored project editor window / evaluation window
 - general linting and cleanup
### Fixed
 - bug in observed baseline pressure reporting
 - the Live Plot stops updating (clearing itself) at the end of a test
### Removed
 - dependency on openpyxl
 - ability to export report as .xlsx directly
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