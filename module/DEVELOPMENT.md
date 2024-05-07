# Developing the PRC python module

## Running tests

`pytest .`

## Releasing a new version

1. Bump the version number in `pyproject.toml`
1. `pip install build twine`
1. `python -m build`
1. unzip the whl in `dist/` (rename it first) and check that everything inside looks good
1. `twine check dist/*`
1. Upload to TestPyPi: `twine upload -r testpypi dist/*`

A nice doc on how to do this:
https://realpython.com/pypi-publish-python-package/
