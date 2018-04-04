#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckanext.userdatasets.plugin import get_default_action


def organization_list_for_user(context, data_dict):
    '''

    :param context: 
    :param data_dict: 

    '''
    perm = data_dict.get(u'permission')
    if perm in [u'create_dataset', u'update_dataset', u'delete_dataset']:
        # Create a copy of the data dict, and change the request permission to
        # 'read' which will be granted to all members of a group.
        data_dict = dict(data_dict.items() + {u'permission': u'read'}.items())

    fallback = get_default_action(u'get', u'organization_list_for_user')
    return fallback(context, data_dict)
