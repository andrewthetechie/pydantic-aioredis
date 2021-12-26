Development
===========

The `Makefile <./makefile>`_ has useful targets to help setup your
development encironment. We suggest using pyenv to have access to
multiple python versions easily.

Environment Setup
^^^^^^^^^^^^^^^^^


*
  Clone the repo and enter its root folder

.. code-block::

  git clone https://github.com/sopherapps/pydantic-redis.git && cd pydantic-redis

*
  Create a python 3.9 virtual environment and activate it. We suggest
  using `pyenv <https://github.com/pyenv/pyenv>`_ to easily setup
  multiple python environments on multiple versions.

.. code-block::

  # We use the extra python version (3.6, 3.7, 3.8) for tox testing
  pyenv install 3.9.7 3.6.15 3.7.12 3.8.12
  pyenv virtualenv 3.9.7 python-aioredis
  pyenv local python-aioredis 3.6.15 3.7.12 3.8.12

*
  Install the dependencies

 .. code-block::

   make setup

How to Run Tests
^^^^^^^^^^^^^^^^


*
  Run the test command to run tests on only python 3.9

.. code-block::

   pytest

*
  Run the tox command to run all python version tests

.. code-block::

   tox

Test Requirements
^^^^^^^^^^^^^^^^^

Prs should always have tests to cover the change being made. Code
coverage goals for this project are 100% coverage.

Code Linting
^^^^^^^^^^^^

All code should pass Flake8 and be blackened. If you install and setup
pre-commit (done automatically by environment setup), pre-commit will
lint your code for you.

You can run the linting manually with make

.. code-block::

   make lint

CI
--

CI is run via Github Actions on all PRs and pushes to the main branch.

Releases are automatically released by Github Actions to Pypi.
