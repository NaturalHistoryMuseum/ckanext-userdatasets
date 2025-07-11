#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.authz import has_user_permission_for_some_org
from ckan.logic.auth import get_package_object, get_resource_object
from ckan.plugins import toolkit
from ckantools.decorators import auth

from ckanext.userdatasets.logic.auth.auth import (
    user_owns_package_as_member,
)
from ckanext.userdatasets.logic.utils import org_role_is_valid


@auth()
@toolkit.chained_auth_function
def package_create(next_auth, context, data_dict):
    user = context['auth_user_obj']
    if data_dict and 'owner_org' in data_dict:
        if org_role_is_valid(data_dict['owner_org'], user.name):
            return {'success': True}
    else:
        # If there is no organisation, then this should return success if the user can
        # create datasets for *some* organisation (see the ckan implementation), so
        # either if anonymous packages are allowed or if we have member status in any
        # organisation.
        if has_user_permission_for_some_org(user.name, 'read'):
            return {'success': True}

    return next_auth(context, data_dict)


@auth()
@toolkit.chained_auth_function
def resource_create(next_auth, context, data_dict):
    user = context['auth_user_obj']

    # can be routed from other auths without changing the params correctly
    package_id = data_dict.get('package_id')
    if not package_id and data_dict.get('id'):
        resource = get_resource_object(context, data_dict)
        package_id = resource.package_id
    if not package_id:
        raise toolkit.ValidationError(
            toolkit._('No dataset id provided, cannot check auth.')
        )

    package = get_package_object(context, {'id': package_id})
    if user_owns_package_as_member(user, package):
        return {'success': True}
    return next_auth(context, data_dict)


@auth()
@toolkit.chained_auth_function
def resource_view_create(next_auth, context, data_dict):
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

    return next_auth(context, data_dict)


@auth()
@toolkit.chained_auth_function
def package_collaborator_create(next_auth, context, data_dict):
    user = context['auth_user_obj']

    package_id = data_dict.get('id')
    package = get_package_object(context, {'id': package_id})
    if user_owns_package_as_member(user, package):
        return {'success': True}

    return next_auth(context, data_dict)
