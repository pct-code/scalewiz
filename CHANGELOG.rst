Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`__, and this project
adheres to `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`__.


[v0.5.3]
--------

Fixed
~~~~~

 - a bug in the uptake cycle, plus come cleaning


[v0.5.2]
--------

Fixed
~~~~~

 - issue with packaging the app's icon file

[v0.5.1]
--------

Added
~~~~~

- flowrate controls


[v0.5.0]
--------

Added
~~~~~

- support for a config file

 - can set default experiment parameters for new projects
 - remember the most recent analyst name
 - auto-load the most recent project on startup

- make sure a project is only loaded to one system at a time to prevent data loss

Changed
~~~~~~~

- improved entry validation for project experiment parameters
- non-psi project experiment parameters now accept non-integer values
- chemical treating rates can now be non-integer (eg. 10.5 ppm)


[v0.4.0]
--------

Changed
~~~~~~~

-  major performance / accuracy improvement to readings collection
-  updated pump interface to use py-hplc v0.1.6
-  improved logging implementation
-  improved documentation ### Removed
-  some smelly / unused code

[v0.3.0]
--------

Changed
~~~~~~~

-  moved code for pump interfacing to its own package: py-hplc ### Added
-  dependency on py-hplc

[v0.2.1]
--------

Added
~~~~~

-  entry validation ensuring only numeric inputs are obtained when
   necessary ### Changed
-  refactored some UI rendering

[v0.2.0]
--------

Added
~~~~~

-  clicking a date entry label in the 'Project info' view will clear its
   contents
-  report export as CSV (default)
-  report export as flattened JSON (not human readable)
-  more descriptive window titles, all windows get the app icon ###
   Changed
-  performance improvement to evaluation window
-  time resolution improvement to data collection loop
-  rinse windows will be titled after the system they control
-  requests for rinse cycles will be ignored if a test is already
   running
-  the Live Plot scales the limits of its axes to the data collected
-  evaluation windows will title themselves after their test handler and
   project
-  refactored project editor window / evaluation window
-  general linting and cleanup ### Fixed
-  bug in observed baseline pressure reporting
-  the Live Plot stops updating (clearing itself) at the end of a test
   ### Removed
-  dependency on openpyxl
-  ability to export report as .xlsx directly
-  redundant tabs from EvaluationFrame

`v0.1.0 <https://github.com/teauxfu/pct-scalewiz/releases/tag/v0.1.0>`__
------------------------------------------------------------------------

Added
~~~~~

-  rinse dialog, accessible from the menu bar
-  help text, accessible from the menu bar
-  get\_resource function for getting resource files. can be used for
   resources with bundled executables later ### Changed
-  reset versioning to 0.1.0
-  moved project loading functionality to menu bar
