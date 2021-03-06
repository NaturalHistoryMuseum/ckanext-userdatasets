#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import logging

from ckanext.userdatasets.logic.validators import owner_org_validator

import ckan.lib.plugins as lib_plugins
from ckan.logic.validators import owner_org_validator as default_owner_org_validator
from ckan.plugins import toolkit

log = logging.getLogger(u'ckanext.userdatasets')


@toolkit.chained_action
def package_create(next_action, context, data_dict):
    '''
    :param next_action:
    :param context:
    :param data_dict:

    '''
    package_type = data_dict.get(u'type')
    package_plugin = lib_plugins.lookup_package_plugin(package_type)
    if u'schema' in context:
        schema = context[u'schema']
    else:
        schema = package_plugin.create_package_schema()
    # We modify the schema here to replace owner_org_validator by our own
    if u'owner_org' in schema:
        schema[u'owner_org'] = [owner_org_validator if f is default_owner_org_validator
                                else f for f in schema[u'owner_org']]
    context[u'schema'] = schema

    return next_action(context, data_dict)
