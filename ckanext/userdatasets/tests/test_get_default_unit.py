"""Unit tests on the the get_default_auth/action functions in plugin.py"""

import importlib
from nose.tools import assert_is

from ckanext.userdatasets.plugin import get_default_auth, get_default_action

class TestGetDefaultUnit:
    """Unit tests on the the get_default_auth/action functions in plugin.py"""

    def test_get_default_auth(self):
        for action in ['create', 'update', 'delete']:
            default_module = importlib.import_module('ckan.logic.auth' + '.' + action)
            for atype in ['package', 'resource', 'resource_view']:
                fn_name = atype + '_' + action
                assert_is(getattr(default_module, fn_name), get_default_auth(action, fn_name))

    def test_get_default_action(self):
        to_override = [
            ('create', ['package_create']),
            ('update', ['package_update']),
            ('get', ['organization_list_for_user'])
        ]
        for override in to_override:
            default_module = importlib.import_module('ckan.logic.action' + '.' + override[0])
            for fn_name in override[1]:
                assert_is(getattr(default_module, fn_name), get_default_action(override[0], fn_name))