#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckanext.userdatasets.logic.auth.auth import (user_is_member_of_package_org,
                                                  user_owns_package_as_member)
from ckanext.userdatasets.logic.auth.create import (package_create, resource_create,
                                                    resource_view_create)
from ckanext.userdatasets.logic.auth.delete import (package_delete, resource_delete,
                                                    resource_view_delete)
from ckanext.userdatasets.logic.auth.update import (package_update, resource_update,
                                                    resource_view_update)
from mock import patch, MagicMock


class TestAuthActionsUnit(object):
    '''
    Perform unit tests on the auth functions in ckanext.userdatasets.logic.auth
    '''

    @patch(u'ckanext.userdatasets.logic.auth.auth.users_role_for_group_or_org')
    def test_user_is_member_of_package_org(self, mock_users_role):
        '''
        Test ckanext.userdatasets.logic.auth.auth.user_is_member_of_package_org.

        Ensure all the possible combination of parameters always lead to the expected result.
        '''
        tests = [
            {
                u'package': MagicMock(owner_org=u'carrot'),
                u'user': MagicMock(name=u'turtle'),
                u'role': u'member',
                u'result': True
            },
            {
                u'package': MagicMock(owner_org=u'carrot'),
                u'user': MagicMock(name=u'turtle'),
                u'role': u'editor',
                u'result': False
            },
            {
                u'package': MagicMock(owner_org=None),
                u'user': MagicMock(name=u'turtle'),
                u'role': u'member',
                u'result': False
            },
        ]
        for t in tests:
            mock_users_role.return_value = t[u'role']
            assert user_is_member_of_package_org(t[u'user'], t[u'package']) == t[u'result']

    @patch(u'ckanext.userdatasets.logic.auth.auth.users_role_for_group_or_org')
    def test_user_owns_package_as_member(self, mock_users_role):
        '''
        Test ckanext.userdatasets.logic.auth.auth.user_owns_package_as_member

        Ensure all the possible combination of parameters always lead to the expected result.
        '''
        tests = [
            {
                u'user': MagicMock(id=444, name=u'turtle'),
                u'package': MagicMock(creator_user_id=444, owner_org=u'carrot'),
                u'role': u'member',
                u'result': True
            },
            {
                u'user': MagicMock(id=445, name=u'turtle'),
                u'package': MagicMock(creator_user_id=444, owner_org=u'carrot'),
                u'role': u'member',
                u'result': False
            },
            {
                u'user': MagicMock(id=444, name=u'turtle'),
                u'package': MagicMock(creator_user_id=444, owner_org=False),
                u'role': u'member',
                u'result': False
            },
            {
                u'user': MagicMock(id=444, name=u'turtle'),
                u'package': MagicMock(creator_user_id=444, owner_org=u'carrot'),
                u'role': u'editor',
                u'result': False
            }
        ]
        for t in tests:
            mock_users_role.return_value = t[u'role']
            assert user_owns_package_as_member(t[u'user'], t[u'package']) == t[u'result']

    @patch(u'ckanext.userdatasets.logic.auth.create.users_role_for_group_or_org')
    @patch(u'ckanext.userdatasets.logic.auth.create.has_user_permission_for_some_org')
    def test_package_create(self, mock_has_perm, mock_users_role):
        '''
        Test ckanext.userdatasets.logic.auth.create.package_create.

        Ensure all the possible combination of parameters always lead to the expected result.
        '''
        tests = [
            {
                u'context': {
                    u'auth_user_obj': MagicMock(name=u'turtle')
                },
                u'data_dict': {
                    u'owner_org': u'carrot'
                },
                u'role': u'member',
                u'has_perm': True,
                u'result': {
                    u'success': True
                },
            },
            {
                u'context': {
                    u'auth_user_obj': MagicMock(name=u'turtle')
                },
                u'data_dict': {
                    u'owner_org': u'carrot'
                },
                u'role': u'editor',
                u'has_perm': True,
                u'result': u'fallback',
            },
            {
                u'context': {
                    u'auth_user_obj': MagicMock(name=u'turtle')
                },
                u'data_dict': False,
                u'role': u'member',
                u'has_perm': True,
                u'result': {
                    u'success': True
                },
            },
            {
                u'context': {
                    u'auth_user_obj': MagicMock(name=u'turtle')
                },
                u'data_dict': {
                    u'other': u'value'
                },
                u'role': u'member',
                u'has_perm': True,
                u'result': {
                    u'success': True
                },
            },
            {
                u'context': {
                    u'auth_user_obj': MagicMock(name=u'turtle')
                },
                u'data_dict': False,
                u'role': u'member',
                u'has_perm': False,
                u'result': u'fallback',
            },
            {
                u'context': {
                    u'auth_user_obj': MagicMock(name=u'turtle')
                },
                u'data_dict': {
                    u'other': u'value'
                },
                u'role': u'member',
                u'has_perm': False,
                u'result': u'fallback',
            },
        ]
        for t in tests:
            mock_users_role.return_value = t[u'role']
            mock_has_perm.return_value = t[u'has_perm']
            mock_default_auth = MagicMock(return_value=u'fallback')
            result = package_create(mock_default_auth, t[u'context'], t[u'data_dict'])
            assert result == t[u'result']

    @patch(u'ckanext.userdatasets.logic.auth.create.user_is_member_of_package_org')
    @patch(u'ckanext.userdatasets.logic.auth.create.user_owns_package_as_member')
    @patch(u'ckanext.userdatasets.logic.auth.create.get_package_object')
    def test_resource_create(self, mock_get_package, mock_user_owns, mock_user_is_member):
        '''
        Test ckanext.userdatasets.logic.auth.create.resource_create.

        Ensure all routes are tested.
        '''
        tests = [
            {
                u'user_owns': True,
                u'user_is_member': True,
                u'result': {
                    u'success': True
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': True,
                u'result': {
                    u'success': False
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': False,
                u'result': u'fallback'
            },
        ]
        mock_get_package.return_value = 1
        for t in tests:
            mock_user_owns.return_value = t[u'user_owns']
            mock_user_is_member.return_value = t[u'user_is_member']
            mock_default_auth = MagicMock(return_value=u'fallback')
            result = resource_create(mock_default_auth, {u'auth_user_obj': 1}, MagicMock())
            assert result == t[u'result']

    @patch(u'ckanext.userdatasets.logic.auth.create.user_is_member_of_package_org')
    @patch(u'ckanext.userdatasets.logic.auth.create.user_owns_package_as_member')
    @patch(u'ckanext.userdatasets.logic.auth.create.get_resource_object')
    def test_resource_view_create(self, mock_get_resource, mock_user_owns, mock_user_is_member):
        '''
        Test ckanext.userdatasets.logic.auth.create.resource_view_create.

        Ensure all routes are tested.
        '''

        tests = [
            {
                u'user_owns': True,
                u'user_is_member': True,
                u'result': {
                    u'success': True
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': True,
                u'result': {
                    u'success': False
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': False,
                u'result': u'fallback'
            },
        ]
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t[u'user_owns']
            mock_user_is_member.return_value = t[u'user_is_member']
            mock_default_auth = MagicMock(return_value=u'fallback')
            result = resource_view_create(mock_default_auth, {u'auth_user_obj': 1},
                                          {u'resource_id': 1})
            assert result == t[u'result']

    @patch(u'ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch(u'ckanext.userdatasets.logic.auth.update.get_package_object')
    def test_package_update(self, mock_get_package, mock_user_owns):
        '''
        Test ckanext.userdatasets.logic.auth.update.package_update.

        Ensure both success and failure routes are tested.
        '''
        mock_get_package.return_value = 1
        mock_user_owns.return_value = True
        mock_default_auth = MagicMock(return_value=u'fallback')
        result = package_update(mock_default_auth, {u'auth_user_obj': 1}, MagicMock())
        assert result == {u'success': True}
        mock_user_owns.return_value = False
        result = package_update(mock_default_auth, {u'auth_user_obj': 1}, MagicMock())
        assert result == u'fallback'

    @patch(u'ckanext.userdatasets.logic.auth.update.user_is_member_of_package_org')
    @patch(u'ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch(u'ckanext.userdatasets.logic.auth.update.get_resource_object')
    def test_resource_update(self, mock_get_resource, mock_user_owns, mock_user_is_member):
        '''
        Test ckanext.userdatasets.logic.auth.create.resource_update.

        Ensure all routes are tested.
        '''
        tests = [
            {
                u'user_owns': True,
                u'user_is_member': True,
                u'result': {
                    u'success': True
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': True,
                u'result': {
                    u'success': False
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': False,
                u'result': u'fallback'
            },
        ]
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t[u'user_owns']
            mock_user_is_member.return_value = t[u'user_is_member']
            mock_default_auth = MagicMock(return_value=u'fallback')
            assert resource_update(mock_default_auth, {u'auth_user_obj': 1}, {}) == t[u'result']

    @patch(u'ckanext.userdatasets.logic.auth.update.user_is_member_of_package_org')
    @patch(u'ckanext.userdatasets.logic.auth.update.user_owns_package_as_member')
    @patch(u'ckanext.userdatasets.logic.auth.update.get_resource_object')
    @patch(u'ckanext.userdatasets.logic.auth.update.get_resource_view_object')
    def test_resource_view_update(self, mock_get_resource_view, mock_get_resource, mock_user_owns,
                                  mock_user_is_member):
        '''
        Test ckanext.userdatasets.logic.auth.create.resource_view_update.

        Ensure all routes are tested.
        '''
        tests = [
            {
                u'user_owns': True,
                u'user_is_member': True,
                u'result': {
                    u'success': True
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': True,
                u'result': {
                    u'success': False
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': False,
                u'result': u'fallback'
            },
        ]
        mock_get_resource_view.return_value = MagicMock(resource_id=1)
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t[u'user_owns']
            mock_user_is_member.return_value = t[u'user_is_member']
            mock_default_auth = MagicMock(return_value=u'fallback')
            result = resource_view_update(mock_default_auth, {u'auth_user_obj': 1},
                                          {u'resource_id': 1})
            assert result == t[u'result']

    @patch(u'ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch(u'ckanext.userdatasets.logic.auth.delete.get_package_object')
    def test_package_delete(self, mock_get_package, mock_user_owns):
        '''Test ckanext.userdatasets.logic.auth.delete.package_delete.

        Ensure both success and failure routes are tested.
        '''
        mock_get_package.return_value = 1
        mock_user_owns.return_value = True
        mock_default_auth = MagicMock(return_value=u'fallback')
        assert package_delete(mock_default_auth, {u'auth_user_obj': 1}, {}) == {u'success': True}
        mock_user_owns.return_value = False
        assert package_delete(mock_default_auth, {u'auth_user_obj': 1}, {}) == u'fallback'

    @patch(u'ckanext.userdatasets.logic.auth.delete.user_is_member_of_package_org')
    @patch(u'ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch(u'ckanext.userdatasets.logic.auth.delete.get_resource_object')
    def test_resource_delete(self, mock_get_resource, mock_user_owns, mock_user_is_member):
        '''
        Test ckanext.userdatasets.logic.auth.create.resource_delete.

        Ensure all routes are tested.
        '''
        tests = [
            {
                u'user_owns': True,
                u'user_is_member': True,
                u'result': {
                    u'success': True
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': True,
                u'result': {
                    u'success': False
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': False,
                u'result': u'fallback'
            },
        ]
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t[u'user_owns']
            mock_user_is_member.return_value = t[u'user_is_member']
            mock_default_auth = MagicMock(return_value=u'fallback')
            assert resource_delete(mock_default_auth, {u'auth_user_obj': 1}, {}) == t[u'result']

    @patch(u'ckanext.userdatasets.logic.auth.delete.user_is_member_of_package_org')
    @patch(u'ckanext.userdatasets.logic.auth.delete.user_owns_package_as_member')
    @patch(u'ckanext.userdatasets.logic.auth.delete.get_resource_object')
    @patch(u'ckanext.userdatasets.logic.auth.delete.get_resource_view_object')
    def test_resource_view_delete(self, mock_get_resource_view, mock_get_resource, mock_user_owns,
                                  mock_user_is_member):
        '''
        Test ckanext.userdatasets.logic.auth.create.resource_view_delete.

        Ensure all routes are tested.
        '''
        tests = [
            {
                u'user_owns': True,
                u'user_is_member': True,
                u'result': {
                    u'success': True
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': True,
                u'result': {
                    u'success': False
                }
            },
            {
                u'user_owns': False,
                u'user_is_member': False,
                u'result': u'fallback'
            },
        ]
        mock_get_resource_view.return_value = MagicMock(resource_id=1)
        mock_get_resource.return_value = MagicMock(package=1)
        for t in tests:
            mock_user_owns.return_value = t[u'user_owns']
            mock_user_is_member.return_value = t[u'user_is_member']
            mock_default_auth = MagicMock(return_value=u'fallback')
            result = resource_view_delete(mock_default_auth, {u'auth_user_obj': 1},
                                          {u'resource_id': 1})
            assert result == t[u'result']
