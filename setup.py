#!/usr/bin/env python

import os
from setuptools import setup
from setuptools import find_packages

from peluche.__pkg__ import __version__

root = os.path.dirname(__file__)


def read_requirements_file(path):
    path = os.path.join(root, path)

    requirements = []

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('# '):
                continue
            elif line.startswith('-r '):
                requirements += read_requirements_file(line[3:])
            else:
                requirements.append(line)

    return requirements


classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Software Development :: Debuggers',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Software Development :: Testing',
]
requirements = read_requirements_file('requirements.txt')
requirements_test = read_requirements_file('requirements-test.txt')
requirements_dev = read_requirements_file('requirements-dev.txt')
readme = open(os.path.join(root, 'README.md'), 'r').read()


setup(
    version=__version__,

    name='peluche',
    author='Paul Renvoisé',
    author_email='renvoisepaul@gmail.com',
    url='https://github.com/PaulRenvoise/peluche',
    description='',
    long_description=readme,
    classifiers=classifiers,

    packages=find_packages(exclude=('tests', 'tests.*')),

    install_requires=requirements,
    tests_require=requirements_test,
    python_requires='>=3.6.*',
    setup_requires=['pytest-runner'],

    test_suite='tests',

    entry_points='',
    scripts='',
    data_files=[],
    ext_modules=[],
    cmdclass={},

    license='MIT',
)
