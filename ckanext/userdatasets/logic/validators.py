#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.logic.validators import owner_org_validator as default_owner_org_validator
from ckan.plugins import toolkit

from ckanext.userdatasets.logic.utils import org_role_is_valid


def owner_org_validator(key, data, errors, context):
    owner_org = data.get(key)
    if owner_org is not toolkit.missing and owner_org is not None and owner_org != '':
        if context.get('auth_user_obj', None) is not None:
            username = context['auth_user_obj'].name
        else:
            username = context['user']

        if org_role_is_valid(owner_org, username):
            return

    default_owner_org_validator(key, data, errors, context)
