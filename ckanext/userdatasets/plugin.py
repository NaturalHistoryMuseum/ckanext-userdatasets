#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import importlib

from ckan.plugins import SingletonPlugin, implements, interfaces

config = {}


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
        config[u'default_auth_module'] = config.get(u'userdatasets.default_auth_module',
                                                    u'ckan.logic.auth')
        config[u'default_action_module'] = config.get(
            u'userdatasets.default_action_module', u'ckan.logic.action')

    def get_auth_functions(self):
        '''Implementation of IAuthFunctions.get_auth_functions'''
        # We override all of create/update/delete for packages, resources and
        # resource views.
        auth_functions = {}
        for action in [u'create', u'update', u'delete']:
            default_module = importlib.import_module(
                config[u'default_auth_module'] + u'.' + action)
            uds_module = importlib.import_module(
                u'ckanext.userdatasets.logic.auth.' + action)
            for atype in [u'package', u'resource', u'resource_view']:
                fn_name = atype + u'_' + action
                if hasattr(default_module, fn_name) and hasattr(uds_module, fn_name):
                    auth_functions[fn_name] = getattr(uds_module, fn_name)

        return auth_functions

    def get_actions(self):
        '''Implementation of IActions.get_actions'''
        actions = {}
        # Override selected actions.
        to_override = [
            (u'create', [u'package_create']),
            (u'update', [u'package_update']),
            (u'get', [u'organization_list_for_user'])
            ]
        for override in to_override:
            uds_module = importlib.import_module(
                u'ckanext.userdatasets.logic.action.' + override[0])
            for fn_name in override[1]:
                actions[fn_name] = getattr(uds_module, fn_name)

        return actions


def get_default_auth(ftype, function_name):
    '''Return the default auth function

    :param type: The type of auth function (create/update/delete)
    :param function: Name of function. It must exist.
    :param ftype: 
    :param function_name: 
    :returns: The auth function

    '''
    default_module = importlib.import_module(
        config[u'default_auth_module'] + u'.' + ftype)
    return getattr(default_module, function_name)


def get_default_action(ftype, function_name):
    '''Return the default action function

    :param type: The type of action function (create/update/get)
    :param function: Name of function. It must exist.
    :param ftype: 
    :param function_name: 
    :returns: The action function

    '''
    default_module = importlib.import_module(
        config[u'default_action_module'] + u'.' + ftype)
    return getattr(default_module, function_name)
