import importlib
import ckan.plugins as p

from functools import partial


class UserDatasetsPlugin(p.SingletonPlugin):
    """"UserDatasetsPlugin

    This plugin replaces dataset and resource authentication calls to allow
    users with the 'Member' role to create datasets, and edit/delete their
    own datasets (but not others).
    """

    p.implements(p.IAuthFunctions)
    p.implements(p.IActions)
    p.implements(p.IConfigurable)

    def configure(self, config):
        """Implementation of IConfigurable.configure"""
        self.default_auth_module = config.get('userdatasets.default_auth_module', 'ckan.logic.auth')
        self.default_action_module = config.get('userdatasets.default_action_module', 'ckan.logic.action')

    def get_auth_functions(self):
        """Implementation of IAuthFunctions.get_auth_functions"""
        # We override all of create/update/delete for packages, resources and resource views. Our implementation
        # takes the default auth function as first parameter, which we apply here as a partial.
        auth_functions = {}
        for action in ['create', 'update', 'delete']:
            default_module = importlib.import_module(self.default_auth_module + '.' + action)
            uds_module = importlib.import_module('ckanext.userdatasets.logic.auth.' + action)
            for atype in ['package', 'resource', 'resource_view']:
                fn_name = atype + '_' + action
                if hasattr(default_module, fn_name) and hasattr(uds_module, fn_name):
                    default_fn = getattr(default_module, fn_name)
                    uds_fn = getattr(uds_module, fn_name)
                    auth_functions[fn_name] = partial(uds_fn, default_fn)

        return auth_functions

    def get_actions(self):
        """Implementation of IActions.get_actions"""
        actions = {}
        # Override selected actions. Our implementation takes the default auth functions as first parameter, which we
        # apply here as a partial
        to_override = [
            ('create', ['package_create']),
            ('update', ['package_update']),
            ('get', ['organization_list_for_user'])
        ]
        for override in to_override:
            default_module = importlib.import_module(self.default_action_module + '.' + override[0])
            uds_module = importlib.import_module('ckanext.userdatasets.logic.action.' + override[0])
            for fn_name in override[1]:
                default_fn = getattr(default_module, fn_name)
                uds_fn = getattr(uds_module, fn_name)
                actions[fn_name] = partial(uds_fn, default_fn)

        return actions
