#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit


@toolkit.chained_action
def organization_list_for_user(next_action, context, data_dict):
    '''
    :param next_action:
    :param context:
    :param data_dict:

    '''
    perm = data_dict.get(u'permission')
    if perm in [u'create_dataset', u'update_dataset', u'delete_dataset']:
        # Create a copy of the data dict, and change the request permission to
        # 'read' which will be granted to all members of a group.
        data_dict = dict(data_dict.items() + {
            u'permission': u'read'
        }.items())

    return next_action(context, data_dict)
