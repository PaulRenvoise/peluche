#!/usr/bin/env python

import os
from setuptools import setup
from setuptools import find_packages

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
    name='kepler',
    version='0.0.1',
    packages=find_package(),
    description='',
    long_description=readme,
    author='Paul Renvoisé',
    author_email='renvoisepaul@gmail.com',
    url='https://github.com/PaulRenvoise/kepler',
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=requirements_test,
    extras_require=[],
    entry_points='',
    license='MIT',
    test_suite='tests',
    scripts='',
    classifiers=classifiers,
    data_files=[],
    ext_modules=[],
    cmdclass={},
    python_requires='>=3.6.*',
)
