#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.authz import users_role_for_group_or_org


def org_role_is_valid(group_or_org_id, username):
    """
    Determine whether the given user has a valid role in the specified group or
    organisation.

    :param group_or_org_id: ID of a group or organisation
    :param username: username for the user to check
    :returns: True if the role is valid (member, editor, or admin), False otherwise
    :rtype: bool
    """
    role = users_role_for_group_or_org(group_or_org_id, username)
    return role in ['member', 'editor', 'admin']
