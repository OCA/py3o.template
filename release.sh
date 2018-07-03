#!/bin/bash

rm -rf dist/
python setup.py egg_info -RDb "" sdist --formats=gztar bdist_egg bdist_wheel
twine upload -s dist/* 
