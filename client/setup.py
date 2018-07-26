#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup file for multiscale client."""

import os
import re
from setuptools import setup, find_packages

install_reqs = [
    'girder_client>=2.4.0',
]
# FIXME: Add a readme sometime
# with open('README.rst') as f:
#    readme = f.read()

init = os.path.join(
    os.path.dirname(__file__),
    'multiscale_client',
    '__init__.py')
with open(init) as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)

# perform the install
setup(
    name='multiscale-client',
    version=version,
    description='Python client for performing multiscale operations.',
    #    long_description=readme,
    author='Patrick Avery',
    author_email='psavery@buffalo.edu',
    url='http://github.com/psavery/multiscale',
    #    license='Apache 2.0',
    classifiers=[
        #        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        #        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(exclude=('tests.*', 'tests')),
    install_requires=install_reqs,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'multiscale-client = multiscale_client.client:main'
        ]
    }
)
