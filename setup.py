# -*- coding: utf-8 -*-
"""
aecore
======


Quick links
-----------

- `User Guide <http://code.scotchmedia.com/aecore>`_
- `Repository <http://github.com/scotch/aecore>`_
- `Issue Tracker <https://github.com/scotch/aecore/issues>`_

"""
from setuptools import setup

setup(
    name = 'aecore',
    version = '0.1.0',
    license = 'Apache Software License',
    url = 'http://code.scotchmedia.com/aecore',
    description = "Adds Sessions, Users, & a Datastore Config to Google App Engine",
    long_description = __doc__,
    author = 'Kyle Finley',
    author_email = 'kyle.finley@gmail.com',
    zip_safe = True,
    platforms = 'any',
    packages = [
        'aecore',
        ],
    include_package_data=True,
    install_requires=[
        'setuptools',
        ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)