#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

setup(
    name=u'ckanext-userdatasets',
    version=__version__,
    description=u'A CKAN extension that allows organisation members to create datasets, and edit or delete the datasets they have created.',
    long_description=__long_description__,
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Framework :: Flask',
        u'Programming Language :: Python :: 2.7'
    ],
    keywords=u'CKAN data userdatasets',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-userdatasets',
    license=u'GNU GPLv3',
    packages=find_packages(exclude=[u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.userdatasets'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
		u'importlib',
	],
    entry_points= \
        u'''
        [ckan.plugins]
            userdatasets=ckanext.userdatasets.plugin:UserDatasetsPlugin

        ''',
    )
