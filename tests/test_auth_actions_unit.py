#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from unittest.mock import patch, MagicMock

from ckanext.userdatasets.logic.auth.auth import (
    user_is_member_of_package_org,
    user_owns_package_as_member,
)
from ckanext.userdatasets.logic.auth.create import (
    package_create,
    resource_create,
    resource_view_create,
)
from ckanext.userdatasets.logic.auth.delete import (
    package_delete,
    resource_delete,
    resource_view_delete,
)
from ckanext.userdatasets.logic.auth.update import (
    package_update,
    resource_update,
    resource_view_update,
)


class TestAuthActionsUnit(object):
    """
    Perform unit tests on the auth functions in ckanext.userdatasets.logic.auth.
    """

    @patch('ckanext.userdatasets.logic.auth.auth.users_role_for_group_or_org')
    def test_user_is_member_of_package_org(self, mock_users_role):
        """
        Test ckanext.userdatasets.logic.auth.auth.user_is_member_of_package_org.

        Ensure all the possible combination of parameters always lead to the expected
        result.
        """
        tests = [
            {
                'package': MagicMock(owner_org='carrot'),
                'user': MagicMock(name='turtle'),
                'role': 'member',
                'result': True,
            },
            {
                'package': MagicMock(owner_org='carrot'),
                'user': MagicMock(name='turtle'),
                'role': 'editor',
                'result': False,
            },
            {
                'package': MagicMock(owner_org=None),
                'user': MagicMock(name='turtle'),
                'role': 'member',
                'result': False,
            },
        ]
        for t in tests:
            mock_users_role.return_value = t['role']
            assert user_is_member_of_package_org(t['user'], t['package']) == t['result']

    @patch('ckanext.userdatasets.logic.auth.auth.users_role_for_group_or_org')
    def test_user_owns_package_as_member(self, mock_users_role):
        """
        Test ckanext.userdatasets.logic.auth.auth.user_owns_package_as_member.

        Ensure all the possible combination of parameters always lead to the expected
        result.
        """
        tests = [
            {
                'user': MagicMock(id=444, name='turtle'),
                'package': MagicMock(creator_user_id=444, owner_org='carrot'),
                'role': 'member',
                'result': True,
            },
            {
                'user': MagicMock(id=445, name='turtle'),
                'package': MagicMock(creator_user_id=444, owner_org='carrot'),
                'role': 'member',
                'result': False,
            },
            {
                'user': MagicMock(id=444, name='turtle'),
                'package': MagicMock(creator_user_id=444, owner_org=False),
                'role': 'member',
                'result': False,
            },
            {
                'user': MagicMock(id=444, name='turtle'),
                'package': MagicMock(creator_user_id=444, owner_org='carrot'),
                'role': 'editor',
                'result': False,
            },
        ]
        for t in tests:
            mock_users_role.return_value = t['role']
            assert user_owns_package_as_member(t['user'], t['package']) == t['result']

    @patch('ckanext.userdatasets.logic.auth.create.users_role_for_group_or_org')
    @patch('ckanext.userdatasets.logic.auth.create.has_user_permission_for_some_org')
    def test_package_create(self, mock_has_perm, mock_users_role):
        """
        Test ckanext.userdatasets.logic.auth.create.package_create.

        Ensure all the possible combination of parameters always lead to the expected
        result.
        """
        tests = [
            {
                'context': {'auth_user_obj': MagicMock(name='turtle')},
                'data_dict': {'owner_org': 'carrot'},
                'role': 'member',
                'has_perm': True,
                'result': {'success': True},
            },
            {
                'context': {'auth_user_obj': MagicMock(name='turtle')},
                'data_dict': {'owner_org': 'carrot'},
                'role': 'editor',
                'has_perm': True,
                'result': 'fallback',
            },
            {
                'context': {'auth_user_obj': MagicMock(name='turtle')},
                'data_dict': False,
                'role': 'member',
                'has_perm': True,
                'result': {'success': True},
            },
            {
                'context': {'auth_user_obj': MagicMock(name='turtle')},
                'data_dict': {'other': 'value'},
                'role': 'member',
                'has_perm': True,
                'result': {'success': True},
            },
            {
                'context': {'auth_user_obj': MagicMock(name='turtle')},
                'data_dict': False,
                'role': 'member',
                'has_perm': False,
                'result': 'fallback',
            },
            {
                'context': {'auth_user_obj': MagicMock(name='turtle')},
                'data_dict': {'other': 'value'},
                'role': 'member',
                'has_perm': False,
                'result': 'fallback',
            },
        ]
        for t in tests:
            mock_users_role.return_value = t['role']
            mock_has_perm.return_value = t['has_perm']
            mock_default_auth = MagicMock(return_value='fallback')
            result = package_create(mock_default_auth, t['context'], t['data_dict'])
            assert result == t['result']

    @patch('ckanext.userdatasets.logic.auth.create.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.create.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.create.get_package_object')
    def test_resource_create(
        self, mock_get_package, mock_user_owns, mock_user_is_member
    ):
        """
        Test ckanext.userdatasets.logic.auth.create.resource_create.

        Ensure all routes are tested.
        """
        tests = [
            {'user_owns': True, 'user_is_member': True, 'result': {'success': True}},
            {'user_owns': False, 'user_is_member': True, 'result': {'success': False}},
            {'user_owns': False, 'user_is_member': False, 'result': 'fallback'},
        ]
        mock_get_package.return_value = 1
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            mock_default_auth = MagicMock(return_value='fallback')
            result = resource_create(
                mock_default_auth, {'auth_user_obj': 1}, MagicMock()
            )
            assert result == t['result']

    @patch('ckanext.userdatasets.logic.auth.create.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.create.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.create.get_resource_object')
    def test_resource_view_create(
        self, mock_get_resource, mock_user_owns, mock_user_is_member
    ):
        """
        Test ckanext.userdatasets.logic.auth.create.resource_view_create.

        Ensure all routes are tested.
        """

        tests = [
            {'user_owns': True, 'user_is_member': True, 'result': {'success': True}},
            {'user_owns': False, 'user_is_member': True, 'result': {'success': False}},
            {'user_owns': False, 'user_is_member': False, 'result': 'fallback'},
        ]
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            mock_default_auth = MagicMock(return_value='fallback')
            result = resource_view_create(
                mock_default_auth, {'auth_user_obj': 1}, {'resource_id': 1}
            )
            assert result == t['result']

    @patch('ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.update.get_package_object')
    def test_package_update(self, mock_get_package, mock_user_owns):
        """
        Test ckanext.userdatasets.logic.auth.update.package_update.

        Ensure both success and failure routes are tested.
        """
        mock_get_package.return_value = 1
        mock_user_owns.return_value = True
        mock_default_auth = MagicMock(return_value='fallback')
        result = package_update(mock_default_auth, {'auth_user_obj': 1}, MagicMock())
        assert result == {'success': True}
        mock_user_owns.return_value = False
        result = package_update(mock_default_auth, {'auth_user_obj': 1}, MagicMock())
        assert result == 'fallback'

    @patch('ckanext.userdatasets.logic.auth.update.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.update.get_resource_object')
    def test_resource_update(
        self, mock_get_resource, mock_user_owns, mock_user_is_member
    ):
        """
        Test ckanext.userdatasets.logic.auth.create.resource_update.

        Ensure all routes are tested.
        """
        tests = [
            {'user_owns': True, 'user_is_member': True, 'result': {'success': True}},
            {'user_owns': False, 'user_is_member': True, 'result': {'success': False}},
            {'user_owns': False, 'user_is_member': False, 'result': 'fallback'},
        ]
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            mock_default_auth = MagicMock(return_value='fallback')
            assert (
                resource_update(mock_default_auth, {'auth_user_obj': 1}, {})
                == t['result']
            )

    @patch('ckanext.userdatasets.logic.auth.update.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.update.get_resource_object')
    @patch('ckanext.userdatasets.logic.auth.update.get_resource_view_object')
    def test_resource_view_update(
        self,
        mock_get_resource_view,
        mock_get_resource,
        mock_user_owns,
        mock_user_is_member,
    ):
        """
        Test ckanext.userdatasets.logic.auth.create.resource_view_update.

        Ensure all routes are tested.
        """
        tests = [
            {'user_owns': True, 'user_is_member': True, 'result': {'success': True}},
            {'user_owns': False, 'user_is_member': True, 'result': {'success': False}},
            {'user_owns': False, 'user_is_member': False, 'result': 'fallback'},
        ]
        mock_get_resource_view.return_value = MagicMock(resource_id=1)
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            mock_default_auth = MagicMock(return_value='fallback')
            result = resource_view_update(
                mock_default_auth, {'auth_user_obj': 1}, {'resource_id': 1}
            )
            assert result == t['result']

    @patch('ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.delete.get_package_object')
    def test_package_delete(self, mock_get_package, mock_user_owns):
        """
        Test ckanext.userdatasets.logic.auth.delete.package_delete.

        Ensure both success and failure routes are tested.
        """
        mock_get_package.return_value = 1
        mock_user_owns.return_value = True
        mock_default_auth = MagicMock(return_value='fallback')
        assert package_delete(mock_default_auth, {'auth_user_obj': 1}, {}) == {
            'success': True
        }
        mock_user_owns.return_value = False
        assert package_delete(mock_default_auth, {'auth_user_obj': 1}, {}) == 'fallback'

    @patch('ckanext.userdatasets.logic.auth.delete.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.delete.get_resource_object')
    def test_resource_delete(
        self, mock_get_resource, mock_user_owns, mock_user_is_member
    ):
        """
        Test ckanext.userdatasets.logic.auth.create.resource_delete.

        Ensure all routes are tested.
        """
        tests = [
            {'user_owns': True, 'user_is_member': True, 'result': {'success': True}},
            {'user_owns': False, 'user_is_member': True, 'result': {'success': False}},
            {'user_owns': False, 'user_is_member': False, 'result': 'fallback'},
        ]
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            mock_default_auth = MagicMock(return_value='fallback')
            assert (
                resource_delete(mock_default_auth, {'auth_user_obj': 1}, {})
                == t['result']
            )

    @patch('ckanext.userdatasets.logic.auth.delete.user_is_member_of_package_org')
    @patch('ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch('ckanext.userdatasets.logic.auth.delete.get_resource_object')
    @patch('ckanext.userdatasets.logic.auth.delete.get_resource_view_object')
    def test_resource_view_delete(
        self,
        mock_get_resource_view,
        mock_get_resource,
        mock_user_owns,
        mock_user_is_member,
    ):
        """
        Test ckanext.userdatasets.logic.auth.create.resource_view_delete.

        Ensure all routes are tested.
        """
        tests = [
            {'user_owns': True, 'user_is_member': True, 'result': {'success': True}},
            {'user_owns': False, 'user_is_member': True, 'result': {'success': False}},
            {'user_owns': False, 'user_is_member': False, 'result': 'fallback'},
        ]
        mock_get_resource_view.return_value = MagicMock(resource_id=1)
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t['user_owns']
            mock_user_is_member.return_value = t['user_is_member']
            mock_default_auth = MagicMock(return_value='fallback')
            result = resource_view_delete(
                mock_default_auth, {'auth_user_obj': 1}, {'resource_id': 1}
            )
            assert result == t['result']
