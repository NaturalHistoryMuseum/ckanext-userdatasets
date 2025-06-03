#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK


from ckan.plugins import SingletonPlugin, implements, interfaces
from ckantools.loaders import create_actions, create_auth


class UserDatasetsPlugin(SingletonPlugin):
    """
    "UserDatasetsPlugin.

    This plugin replaces dataset and resource authentication calls to allow users with
    the 'Member' role to create datasets, and edit/delete their own datasets (but not
    others).
    """

    implements(interfaces.IAuthFunctions)
    implements(interfaces.IActions)

    # IAuthFunctions
    def get_auth_functions(self):
        """
        Implementation of IAuthFunctions.get_auth_functions.
        """
        from ckanext.userdatasets.logic.auth import create, delete, update

        auth = create_auth(create, delete, update)
        return auth

    # IActions
    def get_actions(self):
        """
        Implementation of IActions.get_actions.
        """
        from ckanext.userdatasets.logic.action import create, get, update

        actions = create_actions(create, get, update)
        return actions
