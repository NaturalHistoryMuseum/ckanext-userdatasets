#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import ckan.lib.navl.dictization_functions as df
from ckan.new_authz import users_role_for_group_or_org
from ckan.logic.validators import owner_org_validator as default_oov

missing = df.missing

def owner_org_validator(key, data, errors, context):
    '''

    :param key: 
    :param data: 
    :param errors: 
    :param context: 

    '''
    owner_org = data.get(key)
    user = context[u'auth_user_obj']
    if owner_org is not missing and owner_org is not None and owner_org != u'':
        role = users_role_for_group_or_org(owner_org, user.name)
        if role == u'member':
            return

    default_oov(key, data, errors, context)
