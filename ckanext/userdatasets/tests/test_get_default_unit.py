
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import importlib
from nose.tools import assert_is

from ckanext.userdatasets.plugin import get_default_auth, get_default_action

class TestGetDefaultUnit:
    '''Unit tests on the the get_default_auth/action functions in plugin.py'''

    def test_get_default_auth(self):
        ''' '''
        for action in [u'create', u'update', u'delete']:
            default_module = importlib.import_module(u'ckan.logic.auth' + u'.' + action)
            for atype in [u'package', u'resource', u'resource_view']:
                fn_name = atype + u'_' + action
                assert_is(getattr(default_module, fn_name), get_default_auth(action, fn_name))

    def test_get_default_action(self):
        ''' '''
        to_override = [
            (u'create', [u'package_create']),
            (u'update', [u'package_update']),
            (u'get', [u'organization_list_for_user'])
        ]
        for override in to_override:
            default_module = importlib.import_module(u'ckan.logic.action' + u'.' + override[0])
            for fn_name in override[1]:
                assert_is(getattr(default_module, fn_name), get_default_action(override[0], fn_name))
