from setuptools import find_packages, setup

setup(
    name='scorer_worker_combined_example',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
)
