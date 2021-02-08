#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.authz import has_user_permission_for_some_org, users_role_for_group_or_org
from ckan.logic.auth import get_package_object, get_resource_object
from ckan.plugins import toolkit
from ckanext.userdatasets.logic.auth.auth import (user_is_member_of_package_org,
                                                  user_owns_package_as_member)


@toolkit.chained_auth_function
def package_create(next_auth, context, data_dict):
    '''
    :param next_auth:
    :param context:
    :param data_dict:

    '''
    user = context[u'auth_user_obj']
    if data_dict and u'owner_org' in data_dict:
        role = users_role_for_group_or_org(data_dict[u'owner_org'], user.name)
        if role == u'member':
            return {
                u'success': True
            }
    else:
        # If there is no organisation, then this should return success if the user can
        # create datasets for *some* organisation (see the ckan implementation), so
        # either if anonymous packages are allowed or if we have member status in any
        # organisation.
        if has_user_permission_for_some_org(user.name, u'read'):
            return {
                u'success': True
            }

    return next_auth(context, data_dict)


@toolkit.chained_auth_function
def resource_create(next_auth, context, data_dict):
    '''

    :param context:
    :param data_dict:

    '''
    user = context[u'auth_user_obj']
    package = get_package_object(context, {
        u'id': data_dict[u'package_id']
    })
    if user_owns_package_as_member(user, package):
        return {
            u'success': True
        }
    elif user_is_member_of_package_org(user, package):
        return {
            u'success': False
        }
    return next_auth(context, data_dict)


@toolkit.chained_auth_function
def resource_view_create(next_auth, context, data_dict):
    '''
    :param next_auth:
    :param context:
    :param data_dict:

    '''
    user = context[u'auth_user_obj']
    # data_dict provides 'resource_id', while get_resource_object expects 'id'. This is
    # not consistent with the rest of the API - so future proof it by catering for both
    # cases in case the API is made consistent (one way or the other) later.
    if data_dict and u'resource_id' in data_dict:
        dc = {
            u'id': data_dict[u'resource_id'],
            u'resource_id': data_dict[u'resource_id']
        }
    elif data_dict and u'id' in data_dict:
        dc = {
            u'id': data_dict[u'id'],
            u'resource_id': data_dict[u'id']
        }
    else:
        dc = data_dict
    resource = get_resource_object(context, dc)
    if user_owns_package_as_member(user, resource.package):
        return {
            u'success': True
        }
    elif user_is_member_of_package_org(user, resource.package):
        return {
            u'success': False
        }

    return next_auth(context, data_dict)
