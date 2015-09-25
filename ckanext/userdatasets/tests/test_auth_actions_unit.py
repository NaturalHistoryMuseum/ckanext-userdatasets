"""Unit tests on the auth functions in ckanext.userdatasets.logic.auth

   These tests test the auth functions' implementation independently of CKAN.
    For that reason the CKAN calls are patched.

    The first two tests check ckanext.userdatasets.auth.auth.user_owns_package_as_member and
    ckanext.userdatasets.auth.auth.user_is_member_of_package_org extensively;
    these function are then patched when testing the auth functions to ensure that each function's
    logic is tested rather than re-testing user_owns_package_as_member each time.
"""
from mock import patch, Mock
from nose import SkipTest
from nose.tools import assert_equal

from ckanext.userdatasets.logic.auth.auth import user_owns_package_as_member, user_is_member_of_package_org
from ckanext.userdatasets.logic.auth.create import package_create, resource_create, resource_view_create
from ckanext.userdatasets.logic.auth.update import package_update, resource_update, resource_view_update
from ckanext.userdatasets.logic.auth.delete import package_delete, resource_delete, resource_view_delete


class SMock:
    def __init__(self, **k):
        for i in k:
            setattr(self, i, k[i])


class TestAuthActionsUnit:
    """Perform unit tests on the auth functions in ckanext.userdatasets.logic.auth"""

    @classmethod
    def setup_class(cls):
        # Check whether this version of CKAN has resource views.  Remove this test when branch 1251 gets merged into CKAN master.
        try:
            from ckan.logic.action.create import resource_view_create
            cls.has_resource_views = True
        except ImportError:
            cls.has_resource_views = False

    @patch('ckanext.userdatasets.logic.auth.auth.users_role_for_group_or_org')
    def test_user_is_member_of_package_org(self, mock_users_role):
        """Test ckanext.userdatasets.logic.auth.auth.user_is_member_of_package_org

        Ensure all the possible combination of parameters always lead to the expected
        result.
        """
        tests = [
            {
                'package': SMock(owner_org='carrot'),
                'user': SMock(name='turtle'),
                'role': 'member',
                'result': True
            },
            {
                'package': SMock(owner_org='carrot'),
                'user': SMock(name='turtle'),
                'role': 'editor',
                'result': False
            },
            {
                'package': SMock(owner_org=None),
                'user': SMock(name='turtle'),
                'role': 'member',
                'result': False
            },
        ]
        for t in tests:
            mock_users_role.return_value = t['role']
            assert_equal(user_is_member_of_package_org(t['user'], t['package']), t['result'])

    @patch('ckanext.userdatasets.logic.auth.auth.users_role_for_group_or_org')
    def test_user_owns_package_as_member(self, mock_users_role):
        """Test ckanext.userdatasets.logic.auth.auth.user_owns_package_as_member

        Ensure all the possible combination of parameters always lead to the expected
        result.
        """
        tests = [
            {
                'user': SMock(id=444, name='turtle'),
                'package': SMock(creator_user_id=444, owner_org='carrot'),
                'role': 'member',
                'result': True
            },
            {
                'user': SMock(id=445, name='turtle'),
                'package': SMock(creator_user_id=444, owner_org='carrot'),
                'role': 'member',
                'result': False
            },
            {
                'user': SMock(id=444, name='turtle'),
                'package': SMock(creator_user_id=444, owner_org=False),
                'role': 'member',
                'result': False
            },
            {
                'user': SMock(id=444, name='turtle'),
                'package': SMock(creator_user_id=444, owner_org='carrot'),
                'role': 'editor',
                'result': False
            }
        ]
        for t in tests:
            mock_users_role.return_value = t['role']
            assert_equal(user_owns_package_as_member(t['user'], t['package']), t['result'])

    @patch('ckanext.userdatasets.logic.auth.create.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.create.users_role_for_group_or_org')
    @patch('ckanext.userdatasets.logic.auth.create.has_user_permission_for_some_org')
    def test_package_create(self, mock_has_perm, mock_users_role, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.create.package_create.

        Ensure all the possible combination of parameters always lead to the expected
        result.
        """
        tests = [
            {
                'context': {'auth_user_obj': SMock(name='turtle')},
                'data_dict': {'owner_org': 'carrot'},
                'role': 'member',
                'has_perm': True,
                'result': {'success': True},
            },
            {
                'context': {'auth_user_obj': SMock(name='turtle')},
                'data_dict': {'owner_org': 'carrot'},
                'role': 'editor',
                'has_perm': True,
                'result': 'fallback',
            },
            {
                'context': {'auth_user_obj': SMock(name='turtle')},
                'data_dict': False,
                'role': 'member',
                'has_perm': True,
                'result': {'success': True},
            },
            {
                'context': {'auth_user_obj': SMock(name='turtle')},
                'data_dict': {'other':'value'},
                'role': 'member',
                'has_perm': True,
                'result': {'success': True},
            },
            {
                'context': {'auth_user_obj': SMock(name='turtle')},
                'data_dict': False,
                'role': 'member',
                'has_perm': False,
                'result': 'fallback',
            },
            {
                'context': {'auth_user_obj': SMock(name='turtle')},
                'data_dict': {'other':'value'},
                'role': 'member',
                'has_perm': False,
                'result': 'fallback',
            },
        ]
        for t in tests:
            mock_users_role.return_value = t['role']
            mock_has_perm.return_value = t['has_perm']
            mock_default_auth.return_value = Mock(return_value='fallback')
            assert_equal(package_create(t['context'], t['data_dict']), t['result'])

    @patch('ckanext.userdatasets.logic.auth.create.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.create.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.create.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.create.get_package_object')
    def test_resource_create(self, mock_get_package, mock_user_owns, mock_user_is_member, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.create.resource_create.

        Ensure all routes are tested.
        """
        tests = [
            {
                'user_owns': True,
                'user_is_member': True,
                'result': {'success': True}
            },
            {
                'user_owns': False,
                'user_is_member': True,
                'result': {'success': False}
            },
            {
                'user_owns': False,
                'user_is_member': False,
                'result': 'fallback'
            },
        ]
        mock_get_package.return_value = 1
        mock_default_auth.return_value = Mock(return_value='fallback')
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            assert_equal(resource_create({'auth_user_obj': 1}, {}), t['result'])

    @patch('ckanext.userdatasets.logic.auth.create.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.create.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.create.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.create.get_resource_object')
    def test_resource_view_create(self, mock_get_resource, mock_user_owns, mock_user_is_member, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.create.resource_view_create.

        Ensure all routes are tested.
        """
        if not self.has_resource_views:
            raise SkipTest("This version of CKAN does not have resource views")

        tests = [
            {
                'user_owns': True,
                'user_is_member': True,
                'result': {'success': True}
            },
            {
                'user_owns': False,
                'user_is_member': True,
                'result': {'success': False}
            },
            {
                'user_owns': False,
                'user_is_member': False,
                'result': 'fallback'
            },
        ]
        mock_get_resource.return_value = SMock(package=1)
        mock_default_auth.return_value = Mock(return_value='fallback')
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            assert_equal(resource_view_create({'auth_user_obj': 1}, {'resource_id':1}), t['result'])

    @patch('ckanext.userdatasets.logic.auth.update.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.update.get_package_object')
    def test_package_update(self, mock_get_package, mock_user_owns, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.update.package_update.

        Ensure both success and failure routes are tested.
        """
        mock_get_package.return_value = 1
        mock_user_owns.return_value = True
        assert_equal(package_update({'auth_user_obj': 1}, {}), {'success': True})
        mock_user_owns.return_value = False
        mock_default_auth.return_value = Mock(return_value='fallback')
        assert_equal(package_update({'auth_user_obj': 1}, {}), 'fallback')

    @patch('ckanext.userdatasets.logic.auth.update.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.update.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.update.get_resource_object')
    def test_resource_update(self, mock_get_resource, mock_user_owns, mock_user_is_member, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.create.resource_update.

        Ensure all routes are tested.
        """
        tests = [
            {
                'user_owns': True,
                'user_is_member': True,
                'result': {'success': True}
            },
            {
                'user_owns': False,
                'user_is_member': True,
                'result': {'success': False}
            },
            {
                'user_owns': False,
                'user_is_member': False,
                'result': 'fallback'
            },
        ]
        mock_get_resource.return_value = SMock(package=1)
        mock_default_auth.return_value = Mock(return_value='fallback')
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            assert_equal(resource_update({'auth_user_obj': 1}, {}), t['result'])

    @patch('ckanext.userdatasets.logic.auth.update.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.update.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.update.get_resource_object')
    @patch('ckanext.userdatasets.logic.auth.update.get_resource_view_object')
    def test_resource_view_update(self, mock_get_resource_view, mock_get_resource, mock_user_owns,
                                  mock_user_is_member, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.create.resource_view_update.

        Ensure all routes are tested.
        """
        if not self.has_resource_views:
            raise SkipTest("This version of CKAN does not have resource views")

        tests = [
            {
                'user_owns': True,
                'user_is_member': True,
                'result': {'success': True}
            },
            {
                'user_owns': False,
                'user_is_member': True,
                'result': {'success': False}
            },
            {
                'user_owns': False,
                'user_is_member': False,
                'result': 'fallback'
            },
        ]
        mock_get_resource_view.return_value = SMock(resource_id=1)
        mock_get_resource.return_value = SMock(package=1)
        mock_default_auth.return_value = Mock(return_value='fallback')
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            assert_equal(resource_view_update({'auth_user_obj': 1}, {'resource_id':1}), t['result'])

    @patch('ckanext.userdatasets.logic.auth.delete.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.delete.get_package_object')
    def test_package_delete(self, mock_get_package, mock_user_owns, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.delete.package_delete.

        Ensure both success and failure routes are tested.
        """
        mock_get_package.return_value = 1
        mock_user_owns.return_value = True
        assert_equal(package_delete({'auth_user_obj': 1}, {}), {'success': True})
        mock_user_owns.return_value = False
        mock_default_auth.return_value = Mock(return_value='fallback')
        assert_equal(package_delete({'auth_user_obj': 1}, {}), 'fallback')

    @patch('ckanext.userdatasets.logic.auth.delete.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.delete.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.delete.get_resource_object')
    def test_resource_delete(self, mock_get_resource, mock_user_owns, mock_user_is_member, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.create.resource_delete.

        Ensure all routes are tested.
        """
        tests = [
            {
                'user_owns': True,
                'user_is_member': True,
                'result': {'success': True}
            },
            {
                'user_owns': False,
                'user_is_member': True,
                'result': {'success': False}
            },
            {
                'user_owns': False,
                'user_is_member': False,
                'result': 'fallback'
            },
        ]
        mock_get_resource.return_value = SMock(package=1)
        mock_default_auth.return_value = Mock(return_value='fallback')
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            assert_equal(resource_delete({'auth_user_obj': 1}, {}), t['result'])

    @patch('ckanext.userdatasets.logic.auth.delete.get_default_auth')
    @patch('ckanext.userdatasets.logic.auth.delete.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.delete.get_resource_object')
    @patch('ckanext.userdatasets.logic.auth.delete.get_resource_view_object')
    def test_resource_view_delete(self, mock_get_resource_view, mock_get_resource, mock_user_owns,
                                  mock_user_is_member, mock_default_auth):
        """Test ckanext.userdatasets.logic.auth.create.resource_view_delete.

        Ensure all routes are tested.
        """
        if not self.has_resource_views:
            raise SkipTest("This version of CKAN does not have resource views")

        tests = [
            {
                'user_owns': True,
                'user_is_member': True,
                'result': {'success': True}
            },
            {
                'user_owns': False,
                'user_is_member': True,
                'result': {'success': False}
            },
            {
                'user_owns': False,
                'user_is_member': False,
                'result': 'fallback'
            },
        ]
        mock_get_resource_view.return_value = SMock(resource_id=1)
        mock_get_resource.return_value = SMock(package=1)
        mock_default_auth.return_value = Mock(return_value='fallback')
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            assert_equal(resource_view_delete({'auth_user_obj': 1}, {'resource_id':1}), t['result'])

