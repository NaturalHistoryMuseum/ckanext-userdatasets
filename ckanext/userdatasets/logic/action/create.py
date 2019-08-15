#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import logging

from ckanext.userdatasets.logic.validators import owner_org_validator

import ckan.lib.dictization.model_save as model_save
import ckan.lib.plugins as lib_plugins
from ckan.logic.validators import owner_org_validator as default_owner_org_validator
from ckan.plugins import PluginImplementations, interfaces, toolkit

log = logging.getLogger(__name__)


def package_create(context, data_dict):
    '''

    :param context:
    :param data_dict:

    '''
    model = context[u'model']
    user = context[u'user']

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

    toolkit.check_access(u'package_create', context, data_dict)

    if u'api_version' not in context:
        # check_data_dict() is deprecated. If the package_plugin has a
        # check_data_dict() we'll call it, if it doesn't have the method we'll
        # do nothing.
        check_data_dict = getattr(package_plugin, u'check_data_dict', None)
        if check_data_dict:
            try:
                check_data_dict(data_dict, schema)
            except TypeError:
                # Old plugins do not support passing the schema so we need
                # to ensure they still work
                package_plugin.check_data_dict(data_dict)

    data, errors = lib_plugins.plugin_validate(
        package_plugin, context, data_dict, schema, u'package_create')
    log.debug(u'package_create validate_errs=%r user=%s package=%s data=%r',
              errors, context.get(u'user'),
              data.get(u'name'), data_dict)

    if errors:
        model.Session.rollback()
        raise toolkit.ValidationError(errors)

    rev = model.repo.new_revision()
    rev.author = user
    if u'message' in context:
        rev.message = context[u'message']
    else:
        rev.message = toolkit._(u'REST API: Create object %s') % data.get(u'name')

    admins = []
    if user:
        user_obj = model.User.by_name(user.decode(u'utf8'))
        if user_obj:
            admins = [user_obj]
            data[u'creator_user_id'] = user_obj.id

    pkg = model_save.package_dict_save(data, context)

    # Needed to let extensions know the package id
    model.Session.flush()
    data[u'id'] = pkg.id

    context_org_update = context.copy()
    context_org_update[u'ignore_auth'] = True
    context_org_update[u'defer_commit'] = True
    toolkit.get_action(u'package_owner_org_update')(context_org_update,
                                                    {
                                                        u'id': pkg.id,
                                                        u'organization_id': pkg.owner_org
                                                        })

    for item in PluginImplementations(interfaces.IPackageController):
        item.create(pkg)

        item.after_create(context, data)

    if not context.get(u'defer_commit'):
        model.repo.commit()

    # need to let rest api create
    context[u'package'] = pkg
    # this is added so that the rest controller can make a new location
    context[u'id'] = pkg.id
    log.debug(u'Created object %s' % pkg.name)

    # Make sure that a user provided schema is not used on package_show
    context.pop(u'schema', None)

    return_id_only = context.get(u'return_id_only', False)

    output = context[u'id'] if return_id_only \
        else toolkit.get_action(u'package_show')(context,
                                                 {
                                                     u'id': context[u'id']
                                                     })

    return output
