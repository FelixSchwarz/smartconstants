#!/usr/bin/env python

import re
import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def requires_from_file(filename):
    requirements = []
    with open(filename, 'r') as requirements_fp:
        for line in requirements_fp.readlines():
            match = re.search('^\s*([a-zA-Z][^#]+?)(\s*#.+)?\n$', line)
            if match:
                requirements.append(match.group(1))
    return requirements

setup(
    name = 'SmartConstants',
    version = '1.2.0',
    description = 'magic class to declare easy-to-use "enum"-like values',
    long_description=(read('Changelog.txt')),

    author='Felix Schwarz',
    author_email='felix.schwarz@oss.schwarz.eu',
    license='MIT',
    url='https://github.com/FelixSchwarz/smartconstants/',

    install_requires=requires_from_file('requirements.txt'),
    test_requires=requires_from_file('dev_requirements.txt'),
    test_suite = 'nose.collector',

    py_modules=['smart_constants'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
