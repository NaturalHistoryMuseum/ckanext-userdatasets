#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import paste.fixture
import pylons.test

import ckan.model as model
import ckan.tests as tests
import ckan.plugins as plugins

from nose import SkipTest
from nose.tools import assert_equal

class TestUserdataSetsFunc(object):
    '''Functional tests for the ckanext-userdatasets plugin'''
    @classmethod
    def setup_class(cls):
        ''' '''
        # Check whether this version of CKAN has resource views.  Remove this test when branch 1251 gets merged into CKAN master.
        try:
            from ckan.logic.action.create import resource_view_create
            cls.has_resource_views = True
        except ImportError:
            cls.has_resource_views = False
        # Create the CKAN app and load our plugins
        cls.app = paste.fixture.TestApp(pylons.test.pylonsapp)
        plugins.load(u'userdatasets')
        if cls.has_resource_views:
            plugins.load(u'text_preview')

    @classmethod
    def teardown_class(cls):
        ''' '''
        # Unload our plugin
        plugins.unload(u'userdatasets')

    def setup(self):
        ''' '''
        # Create a sysadmin user
        self.sysadmin = model.User(name=u'test_sysadmin', sysadmin=True)
        model.Session.add(self.sysadmin)
        model.Session.commit()
        model.Session.remove()
        # Create three users: test_member_1, test_member_2 and test_editor
        self.users = {}
        for name in [u'test_member_1', u'test_member_2', u'test_editor']:
            self.users[name] = tests.call_action_api(self.app, u'user_create',
                                                     apikey=self.sysadmin.apikey,
                                                     name=name,
                                                     email=u'email',
                                                     password=u'password')
        # Create the organization test_org_1 of which test_member_1 and test_member_2 are
        # members, and test_editor is an editor
        users = [
            {u'name': u'test_member_1', u'capacity': u'member'},
            {u'name': u'test_member_2', u'capacity': u'member'},
            {u'name': u'test_editor', u'capacity': u'editor'},
        ]
        self.organizations = {}
        self.organizations[u'test_org_1'] = tests.call_action_api(self.app, u'organization_create',
                                               apikey=self.sysadmin.apikey,
                                               name=u'test_org_1',
                                               users=users)
        # Create the organization test_org_2 with no members.
        self.organizations[u'test_org_2'] = tests.call_action_api(self.app, u'organization_create',
                                               apikey=self.sysadmin.apikey,
                                               name=u'test_org_2')

    def teardown(self):
        ''' '''
        # Rebuild the db; each test starts clean.
        model.repo.rebuild_db()

    def test_dataset(self):
        '''Tests datasets'''
        # Create a dataset test_pkg_1 in organization test_org_1 as member test_member_1
        pkg = tests.call_action_api(self.app, u'package_create',
                                    apikey=self.users[u'test_member_1'][u'apikey'],
                                    name=u'test_pkg_1',
                                    owner_org=self.organizations[u'test_org_1'][u'id'])
        assert_equal(pkg[u'name'], u'test_pkg_1')
        # Update the dataset test_pkg_1 as member test_member_1
        pkg = tests.call_action_api(self.app, u'package_update',
                                       apikey=self.users[u'test_member_1'][u'apikey'],
                                       id=pkg[u'id'],
                                       title=u'new title')
        assert_equal(pkg[u'title'], u'new title')
        # Update the dataset test_pkg_1 as member test_editor
        pkg = tests.call_action_api(self.app, u'package_update',
                                       apikey=self.users[u'test_editor'][u'apikey'],
                                       id=pkg[u'id'],
                                       title=u'new title 2')
        assert_equal(pkg[u'title'], u'new title 2')
        # Attempt to update test_pkg_1 as member test_member_2
        result = tests.call_action_api(self.app, u'package_update',
                                       apikey=self.users[u'test_member_2'][u'apikey'],
                                       id=pkg[u'id'],
                                       description=u'new description',
                                       status=403)
        assert_equal(result[u'__type'], u'Authorization Error')
        # Attempt to delete test_pkg_1 as member test_member_2
        result = tests.call_action_api(self.app, u'package_delete',
                                       apikey=self.users[u'test_member_2'][u'apikey'],
                                       id=pkg[u'id'],
                                       status=403)
        assert_equal(result[u'__type'], u'Authorization Error')
        # Delete test_pkg_1 as member test_member_1
        result = tests.call_action_api(self.app, u'package_delete',
                                       apikey=self.users[u'test_member_1'][u'apikey'],
                                       id=pkg[u'id'])
        assert_equal(result, None)
        # Create a dataset test_pkg_2 in organization test_org_1 as member test_member_1
        pkg_2 = tests.call_action_api(self.app, u'package_create',
                                      apikey=self.users[u'test_member_1'][u'apikey'],
                                      name=u'test_pkg_2',
                                      owner_org=self.organizations[u'test_org_1'][u'id'])
        assert_equal(pkg_2[u'name'], u'test_pkg_2')
        # Delete test_pkg_2 as member test_editor
        result = tests.call_action_api(self.app, u'package_delete',
                                       apikey=self.users[u'test_editor'][u'apikey'],
                                       id=pkg_2[u'id'])
        assert_equal(result, None)
        # Attempt to create a dataset test_pkg_3 in organization test_org_2 as member test_member_1
        result = tests.call_action_api(self.app, u'package_create',
                                    apikey=self.users[u'test_member_1'][u'apikey'],
                                    name=u'test_pkg_3',
                                    owner_org=self.organizations[u'test_org_2'][u'id'],
                                    status=403)
        assert_equal(result[u'__type'], u'Authorization Error')

    def test_resource(self):
        '''Tests resources'''
        # Create a dataset test_pkg_1 in organization test_org_1 as member test_member_1
        pkg = tests.call_action_api(self.app, u'package_create',
                                    apikey=self.users[u'test_member_1'][u'apikey'],
                                    name=u'test_pkg_1',
                                    owner_org=self.organizations[u'test_org_1'][u'id'])
        assert_equal(pkg[u'name'], u'test_pkg_1')
        # Create a resource test_res_1 under test_pkg_1 as member test_member_1
        res_1 = tests.call_action_api(self.app, u'resource_create',
                                      apikey=self.users[u'test_member_1'][u'apikey'],
                                      url=u'http://test_res_1.test.com',
                                      package_id=pkg[u'id'])
        assert_equal(res_1[u'url'], u'http://test_res_1.test.com')
        # Update the resource test_res_1 as member test_member_1
        res_1 = tests.call_action_api(self.app, u'resource_update',
                                      apikey=self.users[u'test_member_1'][u'apikey'],
                                      id=res_1[u'id'],
                                      url=u'http://test_res_1.test.com',
                                      description=u'test description')
        assert_equal(res_1[u'description'], u'test description')
        # Update the resource test_res_1 as member test_editor
        res_1 = tests.call_action_api(self.app, u'resource_update',
                                      apikey=self.users[u'test_editor'][u'apikey'],
                                      id=res_1[u'id'],
                                      url=u'http://test_res_1.test.com',
                                      description=u'test description 2')
        assert_equal(res_1[u'description'], u'test description 2')
        # Attempt to update test_res_1 as member test_member_2
        result = tests.call_action_api(self.app, u'resource_update',
                                       apikey=self.users[u'test_member_2'][u'apikey'],
                                       id=res_1[u'id'],
                                       url=u'http://test_res_1.test.com',
                                       description=u'test description 3',
                                       status=403)
        assert_equal(result[u'__type'], u'Authorization Error')
        # Attempt to delete test_res_1 as member test_member_2
        result = tests.call_action_api(self.app, u'resource_delete',
                                       apikey=self.users[u'test_member_2'][u'apikey'],
                                       id=res_1[u'id'],
                                       status=403)
        assert_equal(result[u'__type'], u'Authorization Error')
        # Attempt to create a resource test_res_2 under test_pkg_1 as member test_member_2
        result = tests.call_action_api(self.app, u'resource_create',
                                      apikey=self.users[u'test_member_2'][u'apikey'],
                                      url=u'http://test_res_2.test.com',
                                      package_id=pkg[u'id'],
                                      status=403)
        assert_equal(result[u'__type'], u'Authorization Error')
        # Delete test_res_1 as member test_member_1
        result = tests.call_action_api(self.app, u'resource_delete',
                                       apikey=self.users[u'test_member_1'][u'apikey'],
                                       id=res_1[u'id'])
        assert_equal(result, None)
        # Create a resource test_res_3 under test_pkg_1 as member test_member_1
        res_3 = tests.call_action_api(self.app, u'resource_create',
                                      apikey=self.users[u'test_member_1'][u'apikey'],
                                      url=u'http://test_res_3.test.com',
                                      package_id=pkg[u'id'])
        assert_equal(res_3[u'url'], u'http://test_res_3.test.com')
        # Delete test_res_3 as member test_editor
        result = tests.call_action_api(self.app, u'resource_delete',
                                       apikey=self.users[u'test_editor'][u'apikey'],
                                       id=res_3[u'id'])
        assert_equal(result, None)

    def test_resource_view(self):
        '''Tests resource views'''
        # Only do this if this version of CKAN has resource views.
        if not self.has_resource_views:
            raise SkipTest(u'This version of CKAN does not have resource views')
        # Create a dataset test_pkg_1 in organization test_org_1 as member test_member_1
        pkg = tests.call_action_api(self.app, u'package_create',
                                    apikey=self.users[u'test_member_1'][u'apikey'],
                                    name=u'test_pkg_1',
                                    owner_org=self.organizations[u'test_org_1'][u'id'])
        assert_equal(pkg[u'name'], u'test_pkg_1')
        # Create a resource test_res_1 under test_pkg_1 as member test_member_1
        res_1 = tests.call_action_api(self.app, u'resource_create',
                                      apikey=self.users[u'test_member_1'][u'apikey'],
                                      url=u'http://test_res_1.test.com',
                                      package_id=pkg[u'id'])
        assert_equal(res_1[u'url'], u'http://test_res_1.test.com')
        # Create a resource view test_view_1 under test_rest_1 as member test_member_1
        view_1 = tests.call_action_api(self.app, u'resource_view_create',
                                       apikey=self.users[u'test_member_1'][u'apikey'],
                                       resource_id=res_1[u'id'],
                                       title=u'test view',
                                       view_type=u'text')
        assert_equal(view_1[u'title'], u'test view')
        # Update the resource view test_view_1 as test_member_1
        view_1 = tests.call_action_api(self.app, u'resource_view_update',
                                       apikey=self.users[u'test_member_1'][u'apikey'],
                                       id=view_1[u'id'],
                                       title=u'test view',
                                       description=u'test description',
                                       view_type=u'text')
        assert_equal(view_1[u'description'], u'test description')
        # Update the resource view test_view_1 as test_editor
        view_1 = tests.call_action_api(self.app, u'resource_view_update',
                                       apikey=self.users[u'test_editor'][u'apikey'],
                                       id=view_1[u'id'],
                                       title=u'test view',
                                       description=u'test description 2',
                                       view_type=u'text')
        assert_equal(view_1[u'description'], u'test description 2')
        # Attempt to update test_view_1 as test_member_2
        result = tests.call_action_api(self.app, u'resource_view_update',
                                       apikey=self.users[u'test_member_2'][u'apikey'],
                                       id=view_1[u'id'],
                                       title=u'test view',
                                       description=u'test description 3',
                                       view_type=u'text',
                                       status=403)
        assert_equal(result[u'__type'], u'Authorization Error')
        # Attempt to delete test_view_1 as test_member_2
        result = tests.call_action_api(self.app, u'resource_view_delete',
                                       apikey=self.users[u'test_member_2'][u'apikey'],
                                       id=view_1[u'id'],
                                       status=403)
        assert_equal(result[u'__type'], u'Authorization Error')
        # Attempt to create a resource view test_view_2 under test_res_1 as test_member_2
        result = tests.call_action_api(self.app, u'resource_view_create',
                                       apikey=self.users[u'test_member_2'][u'apikey'],
                                       resource_id=res_1[u'id'],
                                       title=u'test view 2',
                                       view_type=u'text',
                                       status=403)
        assert_equal(result[u'__type'], u'Authorization Error')
        # Delete test_view_1 as test_member_1
        result = tests.call_action_api(self.app, u'resource_view_delete',
                                       apikey=self.users[u'test_member_1'][u'apikey'],
                                       id=view_1[u'id'])
        assert_equal(result, None)
        # Create a resource view test_view_3 under test_rest_1 as member test_member_1
        view_3 = tests.call_action_api(self.app, u'resource_view_create',
                                       apikey=self.users[u'test_member_1'][u'apikey'],
                                       resource_id=res_1[u'id'],
                                       title=u'test view 3',
                                       view_type=u'text')
        assert_equal(view_3[u'title'], u'test view 3')
        # Delete test_view_3 as member test_editor
        result = tests.call_action_api(self.app, u'resource_view_delete',
                                       apikey=self.users[u'test_editor'][u'apikey'],
                                       id=view_3[u'id'])
        assert_equal(result, None)
