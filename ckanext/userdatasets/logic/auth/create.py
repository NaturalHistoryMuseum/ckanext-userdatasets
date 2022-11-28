#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.authz import has_user_permission_for_some_org, users_role_for_group_or_org
from ckan.logic.auth import get_package_object, get_resource_object
from ckan.plugins import toolkit

from ckanext.userdatasets.logic.auth.auth import (
    user_is_member_of_package_org,
    user_owns_package_as_member,
)


@toolkit.chained_auth_function
def package_create(next_auth, context, data_dict):
    '''
    :param next_auth:
    :param context:
    :param data_dict:

    '''
    user = context['auth_user_obj']
    if data_dict and 'owner_org' in data_dict:
        role = users_role_for_group_or_org(data_dict['owner_org'], user.name)
        if role == 'member':
            return {'success': True}
    else:
        # If there is no organisation, then this should return success if the user can
        # create datasets for *some* organisation (see the ckan implementation), so
        # either if anonymous packages are allowed or if we have member status in any
        # organisation.
        if has_user_permission_for_some_org(user.name, 'read'):
            return {'success': True}

    return next_auth(context, data_dict)


@toolkit.chained_auth_function
def resource_create(next_auth, context, data_dict):
    '''

    :param context:
    :param data_dict:

    '''
    user = context['auth_user_obj']
    package = get_package_object(context, {'id': data_dict['package_id']})
    if user_owns_package_as_member(user, package):
        return {'success': True}
    elif user_is_member_of_package_org(user, package):
        return {'success': False}
    return next_auth(context, data_dict)


@toolkit.chained_auth_function
def resource_view_create(next_auth, context, data_dict):
    '''
    :param next_auth:
    :param context:
    :param data_dict:

    '''
    user = context['auth_user_obj']
    # data_dict provides 'resource_id', while get_resource_object expects 'id'. This is
    # not consistent with the rest of the API - so future proof it by catering for both
    # cases in case the API is made consistent (one way or the other) later.
    if data_dict and 'resource_id' in data_dict:
        dc = {'id': data_dict['resource_id'], 'resource_id': data_dict['resource_id']}
    elif data_dict and 'id' in data_dict:
        dc = {'id': data_dict['id'], 'resource_id': data_dict['id']}
    else:
        dc = data_dict
    resource = get_resource_object(context, dc)
    if user_owns_package_as_member(user, resource.package):
        return {'success': True}
    elif user_is_member_of_package_org(user, resource.package):
        return {'success': False}

    return next_auth(context, data_dict)
