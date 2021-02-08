#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.authz import users_role_for_group_or_org

from ckan.logic.validators import owner_org_validator as default_owner_org_validator
from ckan.plugins import toolkit


def owner_org_validator(key, data, errors, context):
    '''

    :param key:
    :param data:
    :param errors:
    :param context:

    '''
    owner_org = data.get(key)
    if owner_org is not toolkit.missing and owner_org is not None and owner_org != u'':
        if context.get(u'auth_user_obj', None) is not None:
            username = context[u'auth_user_obj'].name
        else:
            username = context[u'user']

        role = users_role_for_group_or_org(owner_org, username)
        if role == u'member':
            return

    default_owner_org_validator(key, data, errors, context)
