#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from setuptools import setup, find_packages

version = u'0.1'

setup(
	name=u'ckanext-userdatasets',
	version=version,
	description=u'CKAN extension to allow users to edit their dataset only',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-userdatasets',
	packages=find_packages(),
	namespace_packages=[u'ckanext', u'ckanext.userdatasets'],
	install_requires=[
		u'importlib',
	],	
	entry_points=u'''
        [ckan.plugins]
            userdatasets = ckanext.userdatasets.plugin:UserDatasetsPlugin
	''',
)
