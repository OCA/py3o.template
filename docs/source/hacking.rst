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

We let ``black`` <https://pypi.org/project/black/> take care of everything
here.

Follow its install guide to get it (requires Python 3.6).
Alternatively, the <https://hub.docker.com/r/houzefaabba/python3-black/> Docker
image contains Python 3.6 with ``black`` installed inside.
