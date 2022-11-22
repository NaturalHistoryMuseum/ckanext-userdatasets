#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import importlib

from ckan.plugins import SingletonPlugin, implements, interfaces


class UserDatasetsPlugin(SingletonPlugin):
    """
    "UserDatasetsPlugin.

    This plugin replaces dataset and resource authentication calls to allow users with
    the 'Member' role to create datasets, and edit/delete their own datasets (but not
    others).
    """

    implements(interfaces.IAuthFunctions)
    implements(interfaces.IActions)

    def get_auth_functions(self):
        """
        Implementation of IAuthFunctions.get_auth_functions.
        """
        auth_functions = {}
        for action in ['create', 'update', 'delete']:
            uds_module = importlib.import_module(
                'ckanext.userdatasets.logic.auth.' + action
            )
            for atype in ['package', 'resource', 'resource_view']:
                fn_name = atype + '_' + action
                if hasattr(uds_module, fn_name):
                    auth_functions[fn_name] = getattr(uds_module, fn_name)
        return auth_functions

    def get_actions(self):
        """
        Implementation of IActions.get_actions.
        """
        actions = {}
        # Override selected actions.
        to_override = {
            'create': ['package_create'],
            'update': ['package_update'],
            'get': ['organization_list_for_user'],
        }
        for action_type, action in to_override.items():
            uds_module = importlib.import_module(
                'ckanext.userdatasets.logic.action.' + action_type
            )
            for fn_name in action:
                actions[fn_name] = getattr(uds_module, fn_name)
        return actions
