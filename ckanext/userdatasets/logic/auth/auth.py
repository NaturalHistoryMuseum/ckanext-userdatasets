#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit

from ckanext.userdatasets.logic.utils import org_role_is_valid


def user_is_member_of_package_org(user, package):
    """
    Return True if the package is in an organisation and the user has a valid role in
    that organisation.

    :param user: A user object
    :param package: A package object
    :returns: True if the user has a valid role in the organisation that owns the
        package, False otherwise
    """
    return bool(package.owner_org) and org_role_is_valid(package.owner_org, user.name)


def user_owns_package_as_member(user, package):
    """
    Checks that the given user created the package, and has a valid role in the
    organisation that owns the package.

    :param user: A user object
    :param package: A package object
    :returns: True if the user created the package and has a valid role in the
        organisation to which package belongs. False otherwise.
    """
    if user_is_member_of_package_org(user, package):
        return package.creator_user_id and user.id == package.creator_user_id

    return False


def get_resource_view_object(context, data_dict):
    try:
        return context['resource_view']
    except KeyError:
        model = context['model']
        if not data_dict:
            data_dict = {}
        id = data_dict.get('id', None)
        if not id:
            raise toolkit.ValidationError(
                'Missing id, can not get {0} object'.format('ResourceView')
            )
        obj = getattr(model, 'ResourceView').get(id)
        if not obj:
            raise toolkit.ObjectNotFound
        # Save in case we need this again during the request
        context['resource_view'] = obj
        return obj
