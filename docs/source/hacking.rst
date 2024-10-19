Contributing to py3o.template
=============================

Tests
-----

Tests are easy to run; they rely on ``tox``::

    pip install tox
    tox # Run all tests
    tox -e py3 # Run Python 3 tests only

Tests may also be run via a Python Docker image (same as our CI) through the
``run-tests-via-docker.sh`` script.

Tests reside in ``py3o/template/tests``. To add one:

* Add a test ODT file into ``py3o/template/tests/templates``.
* Add XML expected output into ``py3o/template/tests/templates``. To get it, unzip a
  generated ODT file and take its ``content.xml``.
* Add a ``test_*`` method into ``py3o/template/tests/test_template.py`` that compares
  these (there are many existing tests that do this).

Code style
----------

We let ``pre-commit`` <https://pre-commit.com/> and ``ruff``
<https://pypi.org/project/ruff/> take care of everything here.
