=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project
adheres to `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`_.


[v0.5.9]
--------

Changed
~~~~~~~

UI improvements
===============

- main menu: added a system status label
- rinse window: this functionality was moved into the main menu
- project info window: sizing doesn't break when the project file has a long path
- project report window: can set default pump per-project
- calculations: tweaked scoring formula, log is now more verbose

[v0.5.8]
--------

Hotfix
======

- plot figure saving fixed

[v0.5.7]
--------

Changed
~~~~~~~

User experience
===============

- overhaul the :code:`TestHandlerView` to be better oragnized
- overhaul the :code:`EvaluationWindow` to be better oragnized
- setting labels for each :code:`Test` is now handled in the :code:`EvaluationWindow`s' "Plot" tab
- updated docs
- ensured exported plot dimensions are always uniform

Performance
===========

- updated the :code:`TestHandler` to poll for readings asynchronously
- updated the :code:`TestHandler` to be more robust when generating log files
- minor performance buff to log processing
- minor performance buff to the :code:`LivePlot` component
- minor performance buff to :code:`Project` serialization
- minor performance buff to reading user configuration file

Data handling
=============

- the :code:`Project` data model now records calcium concentration
- updated the :code:`Test` object model to handle the :code:`Reading` class
- updated the :code:`Project` object model to be more backwards compatible
- refactored data analysis out of the :code:`EvaluationWindow` and into its own :code:`score` function
- calculations log is a bit more verbose now
- updated :code:`score` function to handle the :code:`Reading` class

Misc
====

- update all :code:`os.path` operations to fancy :code:`pathlib.Path` operations
- update all :code:`matplotlib` code to use the object oriented API
- fixed some lag that would accumulate when displaying log messages in the main menu
- lots of misc. code cleanup / reorganizing


[v0.5.6]
--------

Added
~~~~~

- added "About" dialog with license info to main menu

Changed
~~~~~~~

- minor performance improvement to Test object model
- improved packaging metadata
- some code cleanup


[v0.5.5]
--------

Changed
~~~~~~~

- licensed under GPLv3

[v0.5.4]
--------

Changed
~~~~~~~

- improvements to packaging

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

- major performance / accuracy improvement to readings collection
- updated pump interface to use py-hplc v0.1.6
- improved logging implementation
- improved documentation ### Removed
- some smelly / unused code

[v0.3.0]
--------

Changed
~~~~~~~

- moved code for pump interfacing to its own package: py-hplc ### Added
- dependency on py-hplc

[v0.2.1]
--------

Added
~~~~~

- entry validation ensuring only numeric inputs are obtained when
   necessary ### Changed
- refactored some UI rendering

[v0.2.0]
--------

Added
~~~~~

- clicking a date entry label in the 'Project info' view will clear its contents
- report export as CSV (default)
- report export as flattened JSON (not human readable)
- more descriptive window titles, all windows get the app icon ###

Changed
~~~~~~~

- performance improvement to evaluation window
- time resolution improvement to data collection loop
- rinse windows will be titled after the system they control
- requests for rinse cycles will be ignored if a test is already running
- the Live Plot scales the limits of its axes to the data collected
- evaluation windows will title themselves after their test handler and project
- refactored project editor window / evaluation window
- general linting and cleanup ### Fixed
- bug in observed baseline pressure reporting
- the Live Plot stops updating (clearing itself) at the end of a test

Removed
~~~~~~~

- dependency on openpyxl
- ability to export report as .xlsx directly
- redundant tabs from EvaluationFrame

[v0.1.0]
------------------------------------------------------------------------

Added
~~~~~

- rinse dialog, accessible from the menu bar
- help text, accessible from the menu bar
- get_resource function for getting resource files. can be used for resources with bundled executables later

Changed
~~~~~~~
- reset versioning to v0.1.0
- moved project loading functionality to menu bar
