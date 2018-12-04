Contributing to py3o.template
=============================

Tests are easy to run; they rely on ``tox``::

    pip install tox
    tox # Run all tests
    tox -e py27 # Run Python 2.7 tests only

Tests reside in ``py3o/tests``. To add one:

* Add a test ODT file into ``py3o/tests/templates``.
* Add XML expected output into ``py3o/tests/templates``. To get it, unzip a
  generated ODT file and take its ``content.xml``.
* Add a ``test_*`` method into ``py3o/tests/test_template.py`` that compares
  these (there are many existing tests that do this).

Code style
----------

TODO
