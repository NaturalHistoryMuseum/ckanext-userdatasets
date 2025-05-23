#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.logic.auth import get_package_object, get_resource_object
from ckan.plugins import toolkit

from ckanext.userdatasets.logic.auth.auth import (
    get_resource_view_object,
    user_owns_package_as_member,
)


@toolkit.chained_auth_function
def package_delete(next_auth, context, data_dict):
    user = context['auth_user_obj']
    package = get_package_object(context, data_dict)

    if user_owns_package_as_member(user, package):
        return {'success': True}

    return next_auth(context, data_dict)


@toolkit.chained_auth_function
def resource_delete(next_auth, context, data_dict):
    user = context['auth_user_obj']
    resource = get_resource_object(context, data_dict)
    package = resource.package
    if user_owns_package_as_member(user, package):
        return {'success': True}

    return next_auth(context, data_dict)


@toolkit.chained_auth_function
def resource_view_delete(next_auth, context, data_dict):
    user = context['auth_user_obj']
    resource_view = get_resource_view_object(context, data_dict)
    resource = get_resource_object(context, {'id': resource_view.resource_id})
    if user_owns_package_as_member(user, resource.package):
        return {'success': True}

    return next_auth(context, data_dict)
