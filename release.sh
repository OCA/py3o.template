#!/bin/bash

rm -rf dist/
python3 setup.py egg_info -Db "" sdist --formats=gztar bdist_wheel
twine upload -s dist/* 
