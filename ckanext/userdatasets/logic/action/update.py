#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import logging

import ckan.lib.plugins as lib_plugins
from ckan.logic.validators import owner_org_validator as default_owner_org_validator
from ckan.plugins import toolkit
from ckanext.userdatasets.logic.validators import owner_org_validator

log = logging.getLogger('ckanext.userdatasets')


@toolkit.chained_action
def package_update(next_action, context, data_dict):
    '''

    :param context:
    :param data_dict:

    '''
    model = context['model']
    name_or_id = data_dict.get('id') or data_dict.get('name')

    pkg = model.Package.get(name_or_id)
    if pkg is None:
        raise toolkit.ObjectNotFound(toolkit._('Package was not found.'))

    toolkit.check_access('package_update', context, data_dict)

    # get the schema
    package_plugin = lib_plugins.lookup_package_plugin(pkg.type)
    if 'schema' in context:
        schema = context['schema']
    else:
        schema = package_plugin.update_package_schema()
    # We modify the schema here to replace owner_org_validator by our own
    if 'owner_org' in schema:
        schema['owner_org'] = [
            owner_org_validator if f is default_owner_org_validator else f
            for f in schema['owner_org']
        ]
    context['schema'] = schema

    return next_action(context, data_dict)
