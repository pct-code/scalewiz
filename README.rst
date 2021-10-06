===========================================================================================
scalewiz |license| |python| |pypi| |build-status| |style| |code quality| |maintainability|
===========================================================================================

A graphical user interface designed to work with `Teledyne SSI MX-class
HPLC pumps`_ for the purpose of calcite scale inhibitor chemical
performance testing.

If you are working with Teledyne SSI Next Generation pumps generally, please check out `py-hplc`_!

If you notice something weird, fragile, or otherwise encounter a bug, please open an `issue`_.

.. image:: https://raw.githubusercontent.com/pct-code/scalewiz/main/img/main_menu.PNG

.. image:: https://raw.githubusercontent.com/pct-code/scalewiz/main/img/evaluation(plot).PNG

Installation
============

ScaleWiz is packaged and run as a GUI, but can be installed like a command-line tool.

::

    python -m pip install --user scalewiz

Or, if you use :code:`pipx` (`try it!`_ 😉) ::

    pipx install scalewiz

Usage
=====

::

    python -m scalewiz

If Python is on your PATH (or you used :code:`pipx` 😎), simply ::

    scalewiz


Further instructions can be viewed in the `docs`_ section of this repo or with the Help button in the main
menu.

Author
======
Written by `@teauxfu`_ for `Premier Chemical Technologies, LLC`_.

Acknowledgements
================
- `@balacla`_ for support and invaluable help in brainstorming

.. |license| image:: https://img.shields.io/github/license/pct-code/scalewiz
  :target: https://github.com/pct-code/py-hplc/blob/main/COPYING
  :alt: GitHub

.. |python| image:: https://img.shields.io/pypi/pyversions/scalewiz
  :alt: PyPI - Python Version

.. |pypi| image:: https://img.shields.io/pypi/v/scalewiz
  :target: https://pypi.org/project/scalewiz/
  :alt: PyPI

.. |build-status| image:: https://github.com/pct-code/scalewiz/actions/workflows/build.yml/badge.svg
  :target: https://github.com/pct-code/scalewiz/actions/workflows/build.yml
  :alt: Build Status

.. |docs| image:: https://readthedocs.org/projects/pip/badge/?version=stable
  :target: https://scalewiz.readthedocs.io/en/latest/
  :alt: Documentation Status

.. |style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/psf/black
  :alt: Style

.. |code quality| image:: https://img.shields.io/badge/code%20quality-flake8-black
  :target: https://gitlab.com/pycqa/flake8
  :alt: Code quality

.. |maintainability| image:: https://api.codeclimate.com/v1/badges/9f4d424afac626a8b2e3/maintainability
   :target: https://codeclimate.com/github/pct-code/scalewiz/maintainability
   :alt: Maintainability


.. _`Premier Chemical Technologies, LLC`: https://premierchemical.tech
.. _`@balacla`: https://github.com/balacla
.. _`@teauxfu`: https://github.com/teauxfu
.. _`Teledyne SSI MX-class HPLC pumps`: https://store.teledynessi.com/collections/mx-class
.. _`py-hplc`: https://github.com/pct-code/py-hplc
.. _`docs`: https://github.com/pct-code/scalewiz/blob/main/doc/index.rst#scalewiz-user-guide
.. _`issue`: https://github.com/pct-code/scalewiz/issues
.. _`try it!`: https://pypa.github.io/pipx/
