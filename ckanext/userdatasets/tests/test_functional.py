"""
Functional tests for the userdatasets plugin

These test ensure that the plugins behave as expected within CKAN. We refer
to 'member', 'editor' and 'admin' as users with the member, editor or admin
role respectively in a given organization.

For each type of object(package, resource, resource_view) this tests that:

    - a given user can create such objects and edit/delete their own objects in
      an organization of which they are a member;

    - editors can edit/delete objects created by members;

    - members cannot edit/delete objects created by other members;

    - users cannot create such object in organizations where they are not
      members.

The actual implementation of the auth functions are tested in a separate
unit test.

"""
import paste.fixture
import pylons.test
import ckan.model as model

# don't use ckan.tests here!
import ckan.tests.legacy as tests

import ckan.plugins as plugins
from nose.tools import assert_equal
import ckan.tests.factories as factories


class TestUserdataSetsFunc(object):
    """Functional tests for the ckanext-userdatasets plugin"""

    @classmethod
    def setup_class(cls):

        # Create the CKAN app and load our plugins
        cls.app = paste.fixture.TestApp(pylons.test.pylonsapp)
        plugins.load('userdatasets', 'text_view')

    @classmethod
    def teardown_class(cls):
        # Unload our plugin
        plugins.unload('userdatasets', 'text_view')

    def setup(self):
        """
        Create users and organizations
        """
        self.sysadmin = factories.Sysadmin()
        self.test_member_1 = factories.User()
        self.test_member_2 = factories.User()
        self.test_editor = factories.User()

        users = [{'name': self.test_member_1['name'], 'capacity': 'member'},
                 {'name': self.test_member_2['name'], 'capacity': 'member'},
                 {'name': self.test_editor['name'], 'capacity': 'editor'}]

        self.test_org_1 = factories.Organization(users=users)
        self.test_org_2 = factories.Organization()

    def teardown(self):
        # Rebuild the db; each test starts clean.
        model.repo.rebuild_db()

    def test_dataset(self):
        """Tests datasets"""

        # Create a dataset test_pkg_1 in organization test_org_1 as member
        # test_member_1
        pkg = tests.call_action_api(self.app, 'package_create',
                                    apikey=self.test_member_1['apikey'],
                                    name='test_pkg_1',
                                    owner_org=self.test_org_1['id'])
        assert_equal(pkg['name'], 'test_pkg_1')

        # Update the dataset test_pkg_1 as member test_member_1
        pkg = tests.call_action_api(self.app, 'package_update',
                                    apikey=self.test_member_1['apikey'],
                                    id=pkg['id'],
                                    title='new title')
        assert_equal(pkg['title'], 'new title')

        # Update the dataset test_pkg_1 as member test_editor
        pkg = tests.call_action_api(self.app, 'package_update',
                                    apikey=self.test_editor['apikey'],
                                    id=pkg['id'],
                                    title='new title 2')
        assert_equal(pkg['title'], 'new title 2')

        # Attempt to update test_pkg_1 as member test_member_2
        result = tests.call_action_api(self.app, 'package_update',
                                       apikey=self.test_member_2['apikey'],
                                       id=pkg['id'],
                                       description='new description',
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

        # Attempt to delete test_pkg_1 as member test_member_2
        result = tests.call_action_api(self.app, 'package_delete',
                                       apikey=self.test_member_2['apikey'],
                                       id=pkg['id'],
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

        # Delete test_pkg_1 as member test_member_1
        result = tests.call_action_api(self.app, 'package_delete',
                                       apikey=self.test_member_1['apikey'],
                                       id=pkg['id'])
        assert_equal(result, None)

        # Create a dataset test_pkg_2 in organization test_org_1 as member
        # test_member_1
        pkg_2 = tests.call_action_api(self.app, 'package_create',
                                      apikey=self.test_member_1['apikey'],
                                      name='test_pkg_2',
                                      owner_org=self.test_org_1['id'])
        assert_equal(pkg_2['name'], 'test_pkg_2')

        # Delete test_pkg_2 as member test_editor
        result = tests.call_action_api(self.app, 'package_delete',
                                       apikey=self.test_editor['apikey'],
                                       id=pkg_2['id'])
        assert_equal(result, None)

        # Attempt to create a dataset test_pkg_3 in organization test_org_2 as
        # member test_member_1
        result = tests.call_action_api(self.app, 'package_create',
                                       apikey=self.test_member_1['apikey'],
                                       name='test_pkg_3',
                                       owner_org=self.test_org_2['id'],
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

    def test_resource(self):
        """Tests resources"""

        # Create a dataset test_pkg_1 in organization test_org_1 as member
        # test_member_1
        pkg = tests.call_action_api(self.app, 'package_create',
                                    apikey=self.test_member_1['apikey'],
                                    name='test_pkg_1',
                                    owner_org=self.test_org_1['id'])
        assert_equal(pkg['name'], 'test_pkg_1')

        # Create a resource test_res_1 under test_pkg_1 as member test_member_1
        res_1 = tests.call_action_api(self.app, 'resource_create',
                                      apikey=self.test_member_1['apikey'],
                                      url='http://test_res_1.test.com',
                                      package_id=pkg['id'])
        assert_equal(res_1['url'], 'http://test_res_1.test.com')

        # Update the resource test_res_1 as member test_member_1
        res_1 = tests.call_action_api(self.app, 'resource_update',
                                      apikey=self.test_member_1['apikey'],
                                      id=res_1['id'],
                                      url='http://test_res_1.test.com',
                                      description='test description')
        assert_equal(res_1['description'], 'test description')

        # Update the resource test_res_1 as member test_editor
        res_1 = tests.call_action_api(self.app, 'resource_update',
                                      apikey=self.test_editor['apikey'],
                                      id=res_1['id'],
                                      url='http://test_res_1.test.com',
                                      description='test description 2')
        assert_equal(res_1['description'], 'test description 2')

        # Attempt to update test_res_1 as member test_member_2
        result = tests.call_action_api(self.app, 'resource_update',
                                       apikey=self.test_member_2['apikey'],
                                       id=res_1['id'],
                                       url='http://test_res_1.test.com',
                                       description='test description 3',
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

        # Attempt to delete test_res_1 as member test_member_2
        result = tests.call_action_api(self.app, 'resource_delete',
                                       apikey=self.test_member_2['apikey'],
                                       id=res_1['id'],
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

        # Attempt to create a resource test_res_2 under test_pkg_1 as member
        # test_member_2
        result = tests.call_action_api(self.app, 'resource_create',
                                       apikey=self.test_member_2['apikey'],
                                       url='http://test_res_2.test.com',
                                       package_id=pkg['id'],
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

        # Delete test_res_1 as member test_member_1
        result = tests.call_action_api(self.app, 'resource_delete',
                                       apikey=self.test_member_1['apikey'],
                                       id=res_1['id'])
        assert_equal(result, None)

        # Create a resource test_res_3 under test_pkg_1 as member test_member_1
        res_3 = tests.call_action_api(self.app, 'resource_create',
                                      apikey=self.test_member_1['apikey'],
                                      url='http://test_res_3.test.com',
                                      package_id=pkg['id'])
        assert_equal(res_3['url'], 'http://test_res_3.test.com')

        # Delete test_res_3 as member test_editor
        result = tests.call_action_api(self.app, 'resource_delete',
                                       apikey=self.test_editor['apikey'],
                                       id=res_3['id'])
        assert_equal(result, None)

    def test_resource_view(self):
        """Tests resource views"""

        # Create a dataset test_pkg_1 in organization test_org_1 as member
        # test_member_1
        pkg = tests.call_action_api(self.app, 'package_create',
                                    apikey=self.test_member_1['apikey'],
                                    name='test_pkg_1',
                                    owner_org=self.test_org_1['id'])
        assert_equal(pkg['name'], 'test_pkg_1')

        # Create a resource test_res_1 under test_pkg_1 as member test_member_1
        res_1 = tests.call_action_api(self.app, 'resource_create',
                                      apikey=self.test_member_1['apikey'],
                                      url='http://test_res_1.test.com',
                                      package_id=pkg['id'])
        assert_equal(res_1['url'], 'http://test_res_1.test.com')

        # Create a resource view test_view_1 under test_rest_1 as member
        # test_member_1
        view_1 = tests.call_action_api(self.app, 'resource_view_create',
                                       apikey=self.test_member_1['apikey'],
                                       resource_id=res_1['id'],
                                       title='test view',
                                       view_type='text_view',
                                       status=200)
        assert_equal(view_1['title'], 'test view')

        # Update the resource view test_view_1 as test_member_1
        view_1 = tests.call_action_api(self.app, 'resource_view_update',
                                       apikey=self.test_member_1['apikey'],
                                       id=view_1['id'],
                                       title='test view',
                                       description='test description',
                                       view_type='text_view')
        assert_equal(view_1['description'], 'test description')

        # Update the resource view test_view_1 as test_editor
        view_1 = tests.call_action_api(self.app, 'resource_view_update',
                                       apikey=self.test_editor['apikey'],
                                       resource_id=res_1['id'],
                                       id=view_1['id'],
                                       title='test view',
                                       description='test description 2',
                                       view_type='text_view')
        assert_equal(view_1['description'], 'test description 2')

        # Attempt to update test_view_1 as test_member_2
        result = tests.call_action_api(self.app, 'resource_view_update',
                                       apikey=self.test_member_2['apikey'],
                                       id=view_1['id'],
                                       title='test view',
                                       description='test description 3',
                                       view_type='text_view',
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

        # Attempt to delete test_view_1 as test_member_2
        result = tests.call_action_api(self.app, 'resource_view_delete',
                                       apikey=self.test_member_2['apikey'],
                                       id=view_1['id'],
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

        # Attempt to create a resource view test_view_2 under test_res_1 as
        # test_member_2
        result = tests.call_action_api(self.app, 'resource_view_create',
                                       apikey=self.test_member_2['apikey'],
                                       resource_id=res_1['id'],
                                       title='test view 2',
                                       view_type='text_view',
                                       status=403)
        assert_equal(result['__type'], 'Authorization Error')

        # Delete test_view_1 as test_member_1
        result = tests.call_action_api(self.app, 'resource_view_delete',
                                       apikey=self.test_member_1['apikey'],
                                       id=view_1['id'])
        assert_equal(result, None)

        # Create a resource view test_view_3 under test_rest_1 as member
        # test_member_1
        view_3 = tests.call_action_api(self.app, 'resource_view_create',
                                       apikey=self.test_member_1['apikey'],
                                       resource_id=res_1['id'],
                                       title='test view 3',
                                       view_type='text_view')
        assert_equal(view_3['title'], 'test view 3')

        # Delete test_view_3 as member test_editor
        result = tests.call_action_api(self.app, 'resource_view_delete',
                                       apikey=self.test_editor['apikey'],
                                       id=view_3['id'])
        assert_equal(result, None)

