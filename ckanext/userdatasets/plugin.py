#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import importlib

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit


class UserDatasetsPlugin(SingletonPlugin):
    '''"UserDatasetsPlugin

    This plugin replaces dataset and resource authentication calls to allow
    users with the 'Member' role to create datasets, and edit/delete their
    own datasets (but not others).

    '''

    implements(interfaces.IAuthFunctions)
    implements(interfaces.IActions)
    implements(interfaces.IConfigurable)

    def configure(self, main_config):
        '''Implementation of IConfigurable.configure

        :param main_config:

        '''
        toolkit.config[u'default_auth_module'] = toolkit.config.get(
            u'userdatasets.default_auth_module',
            u'ckan.logic.auth')
        toolkit.config[u'default_action_module'] = toolkit.config.get(
            u'userdatasets.default_action_module', u'ckan.logic.action')

    def get_auth_functions(self):
        '''Implementation of IAuthFunctions.get_auth_functions'''
        auth_functions = {}
        for action in [u'create', u'update', u'delete']:
            uds_module = importlib.import_module(
                u'ckanext.userdatasets.logic.auth.' + action)
            for atype in [u'package', u'resource', u'resource_view']:
                fn_name = atype + u'_' + action
                if hasattr(uds_module, fn_name):
                    auth_functions[fn_name] = getattr(uds_module, fn_name)
        return auth_functions

    def get_actions(self):
        '''Implementation of IActions.get_actions'''
        actions = {}
        # Override selected actions.
        to_override = {
            u'create': [u'package_create'],
            u'update': [u'package_update'],
            u'get': [u'organization_list_for_user']
            }
        for action_type, action in to_override.items():
            uds_module = importlib.import_module(
                u'ckanext.userdatasets.logic.action.' + action_type)
            for fn_name in action:
                actions[fn_name] = getattr(uds_module, fn_name)
        return actions
