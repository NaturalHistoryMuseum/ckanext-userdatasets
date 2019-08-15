#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckanext.userdatasets.logic.auth.auth import (get_resource_view_object,
                                                  user_is_member_of_package_org,
                                                  user_owns_package_as_member)
from ckanext.userdatasets.lib.helpers import get_default_auth

from ckan.logic.auth import get_package_object, get_resource_object


def package_update(context, data_dict):
    '''

    :param context:
    :param data_dict:

    '''
    user = context[u'auth_user_obj']
    package = get_package_object(context, data_dict)
    if user_owns_package_as_member(user, package):
        return {
            u'success': True
        }

    fallback = get_default_auth(u'update', u'package_update')
    return fallback(context, data_dict)


def resource_update(context, data_dict):
    '''

    :param context:
    :param data_dict:

    '''
    user = context[u'auth_user_obj']
    resource = get_resource_object(context, data_dict)
    package = resource.package
    if user_owns_package_as_member(user, package):
        return {
            u'success': True
        }
    elif user_is_member_of_package_org(user, package):
        return {
            u'success': False
        }

    fallback = get_default_auth(u'update', u'resource_update')
    return fallback(context, data_dict)


def resource_view_update(context, data_dict):
    '''

    :param context:
    :param data_dict:

    '''
    user = context[u'auth_user_obj']
    resource_view = get_resource_view_object(context, data_dict)
    resource = get_resource_object(context, {
        u'id': resource_view.resource_id
    })
    if user_owns_package_as_member(user, resource.package):
        return {
            u'success': True
        }
    elif user_is_member_of_package_org(user, resource.package):
        return {
            u'success': False
        }

    fallback = get_default_auth(u'update', u'resource_view_update')
    return fallback(context, data_dict)
