#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import nose
from ckantest.models import TestBase

from ckan.plugins import toolkit


class TestFuncBase(TestBase):
    '''Functional tests for the ckanext-userdatasets plugin'''
    plugins = [u'userdatasets', u'datastore', u'text_view']

    @classmethod
    def setup_class(cls):
        super(TestFuncBase, cls).setup_class()
        cls._make_users_and_orgs()

    @classmethod
    def _make_users_and_orgs(cls):
        users = [
            {
                u'name': u'test_member_1',
                u'capacity': u'member'
                },
            {
                u'name': u'test_member_2',
                u'capacity': u'member'
                },
            {
                u'name': u'test_editor',
                u'capacity': u'editor'
                },
            ]
        for user in users:
            cls.data_factory().user(name=user[u'name'], password=u'password')

        cls.data_factory().organisation(name=u'test_org_1', users=users)
        cls.data_factory().organisation(name=u'test_org_2')

    def _make_package(self, org=None, user=None, **kwargs):
        data_dict = {}
        if org is not None:
            data_dict.update({
                u'owner_org': self.data_factory().orgs[org][u'id']
                })
        data_dict.update(kwargs)
        context = None if user is None else {
            u'user': user
            }
        pkg_dict = self.data_factory().package(context=context, **data_dict)
        return pkg_dict

    def _make_resource(self, package_id, user=None, **kwargs):
        context = None if user is None else {
            u'user': user
            }
        res_dict = self.data_factory().resource(package_id=package_id, context=context, **kwargs)
        return res_dict

    def _make_resource_view(self, resource_id, user=None, **kwargs):
        context = self.data_factory().context if user is None else {
            u'user': user
            }
        data_dict = {
            u'resource_id': resource_id,
            u'view_type': u'text_view',
            u'title': u'initial resource view title'
            }
        data_dict.update(**kwargs)
        res_view_dict = toolkit.get_action(u'resource_view_create')(context, data_dict)
        return res_view_dict

    def _org_1_member_1(self, resource=False, resource_view=False):
        pkg_dict = self.data_factory().packages.get(u'org_1_member_1', None)
        if pkg_dict is None:
            pkg_dict = self._make_package(org=u'test_org_1', user=u'test_member_1',
                                          name=u'org_1_member_1')
        if not resource and not resource_view:
            return pkg_dict
        res_list = pkg_dict.get(u'resources', [])
        res_dict = res_list[0] if len(res_list) > 0 else self._make_resource(pkg_dict[u'id'],
                                                                             user=u'test_member_1')
        pkg_dict = self.data_factory().packages.get(u'org_1_member_1', None)
        if resource and not resource_view:
            return pkg_dict, res_dict
        res_view_dict = self._make_resource_view(res_dict[u'id'], user=u'test_member_1')
        return pkg_dict, res_dict, res_view_dict


class TestFuncDatasets(TestFuncBase):
    def test_members_can_edit_own_datasets(self):
        '''Tests datasets'''
        pkg_dict = self._org_1_member_1()
        pkg_dict = toolkit.get_action(u'package_update')({
            u'user': u'test_member_1'
            }, {
            u'id': pkg_dict[u'id'],
            u'title': u'title for test_members_can_edit_own_datasets'
            })
        nose.tools.assert_equal(pkg_dict[u'title'], u'title for test_members_can_edit_own_datasets')
        toolkit.get_action(u'package_delete')({
            u'user': u'test_member_1'
            }, {
            u'id': pkg_dict[u'id']
            })

    def test_editors_can_edit_org_datasets(self):
        pkg_dict = self._org_1_member_1()
        pkg_dict = toolkit.get_action(u'package_update')({
            u'user': u'test_editor'
            }, {
            u'id': pkg_dict[u'id'],
            u'title': u'title for test_editors_can_edit_org_datasets'
            })
        nose.tools.assert_equal(pkg_dict[u'title'], u'title for test_editors_can_edit_org_datasets')
        toolkit.get_action(u'package_delete')({
            u'user': u'test_editor'
            }, {
            u'id': pkg_dict[u'id']
            })

    def test_members_cannot_edit_others_datasets(self):
        pkg_dict = self._org_1_member_1()
        # Attempt to update test_pkg_1 as member test_member_2
        with nose.tools.assert_raises_regexp(toolkit.NotAuthorized, u'test_member_2'):
            toolkit.get_action(u'package_update')({
                u'user': u'test_member_2'
                }, {
                u'id': pkg_dict[u'id'],
                u'title': u'title for test_members_cannot_edit_others_datasets'
                })
        # Attempt to delete test_pkg_1 as member test_member_2
        with nose.tools.assert_raises_regexp(toolkit.NotAuthorized, u'test_member_2'):
            toolkit.get_action(u'package_delete')({
                u'user': u'test_member_2'
                }, {
                u'id': pkg_dict[u'id']
                })

    def test_non_members_cannot_create_datasets(self):
        with nose.tools.assert_raises_regexp(toolkit.NotAuthorized, u'test_member_1'):
            self._make_package(org='test_org_2', user='test_member_1')


class TestFuncResources(TestFuncBase):
    def test_members_can_edit_own_resources(self):
        pkg_dict, res_dict = self._org_1_member_1(resource=True)
        nose.tools.assert_greater_equal(len(pkg_dict[u'resources']), 1)

        res_dict = toolkit.get_action(u'resource_update')({
            u'user': u'test_member_1'
            }, {
            u'id': res_dict[u'id'],
            u'description': u'test description 2'
            })
        nose.tools.assert_equal(res_dict[u'description'], u'test description 2')

        toolkit.get_action(u'resource_delete')({
            u'user': u'test_member_1'
            }, {
            u'id': res_dict[u'id']
            })

    def test_editors_can_edit_org_resources(self):
        pkg_dict, res_dict = self._org_1_member_1(resource=True)
        nose.tools.assert_greater_equal(len(pkg_dict[u'resources']), 1)

        res_dict = toolkit.get_action(u'resource_update')({
            u'user': u'test_editor'
            }, {
            u'id': res_dict[u'id'],
            u'description': u'test description for test_editor'
            })
        nose.tools.assert_equal(res_dict[u'description'], u'test description for test_editor')

        toolkit.get_action(u'resource_delete')({
            u'user': u'test_editor'
            }, {
            u'id': res_dict[u'id']
            })

    def test_members_cannot_edit_others_resources(self):
        pkg_dict, res_dict = self._org_1_member_1(resource=True)
        nose.tools.assert_greater_equal(len(pkg_dict[u'resources']), 1)

        context = {
            u'user': u'test_member_2'
            }

        with nose.tools.assert_raises(toolkit.NotAuthorized):
            res_dict = toolkit.get_action(u'resource_update')(context, {
                u'id': res_dict[u'id'],
                u'description': u'this should not work'
                })

        with nose.tools.assert_raises(toolkit.NotAuthorized):
            toolkit.get_action(u'resource_delete')(context, {
                u'id': res_dict[u'id']
                })

        with nose.tools.assert_raises(toolkit.NotAuthorized):
            self.data_factory().resource(package_id=pkg_dict[u'id'],
                                         context=context,
                                         description=u'test description 2')


class TestFuncResourceViews(TestFuncBase):
    def test_members_can_edit_own_resource_views(self):
        pkg_dict, res_dict, res_view_dict = self._org_1_member_1(resource=True, resource_view=True)
        nose.tools.assert_greater_equal(len(pkg_dict[u'resources']), 1)
        nose.tools.assert_equal(res_view_dict[u'view_type'], u'text_view')

        context = {
            u'user': u'test_member_1'
            }
        new_desc = u'description for test_members_can_edit_own_resource_views'
        res_view_dict_2 = toolkit.get_action(u'resource_view_update')(context, {
            u'id': res_view_dict[u'id'],
            u'resource_id': res_dict[u'id'],
            u'description': new_desc
            })
        nose.tools.assert_equal(res_view_dict_2[u'description'], new_desc)
        nose.tools.assert_not_equal(res_view_dict[u'description'], res_view_dict_2[u'description'])

        toolkit.get_action(u'resource_view_delete')(context, {
            u'id': res_view_dict[u'id'],
            u'resource_id': res_dict[u'id']
            })

    def test_editors_can_edit_org_resource_views(self):
        pkg_dict, res_dict, res_view_dict = self._org_1_member_1(resource=True, resource_view=True)
        nose.tools.assert_greater_equal(len(pkg_dict[u'resources']), 1)
        nose.tools.assert_equal(res_view_dict[u'view_type'], u'text_view')

        context = {
            u'user': u'test_editor'
            }
        new_desc = u'description for test_editors_can_edit_org_resource_views'
        res_view_dict_2 = toolkit.get_action(u'resource_view_update')(context, {
            u'id': res_view_dict[u'id'],
            u'resource_id': res_dict[u'id'],
            u'description': new_desc
            })
        nose.tools.assert_equal(res_view_dict_2[u'description'], new_desc)
        nose.tools.assert_not_equal(res_view_dict[u'description'], res_view_dict_2[u'description'])

        toolkit.get_action(u'resource_view_delete')(context, {
            u'id': res_view_dict[u'id'],
            u'resource_id': res_dict[u'id']
            })

    def test_members_cannot_edit_others_resource_views(self):
        pkg_dict, res_dict, res_view_dict = self._org_1_member_1(resource=True, resource_view=True)
        nose.tools.assert_greater_equal(len(pkg_dict[u'resources']), 1)
        nose.tools.assert_equal(res_view_dict[u'view_type'], u'text_view')

        context = {
            u'user': u'test_member_2'
            }
        new_desc = u'description for test_members_cannot_edit_others_resource_views'

        with nose.tools.assert_raises(toolkit.NotAuthorized):
            toolkit.get_action(u'resource_view_update')(context, {
                u'id': res_view_dict[u'id'],
                u'resource_id': res_dict[u'id'],
                u'description': new_desc
                })

        with nose.tools.assert_raises(toolkit.NotAuthorized):
            toolkit.get_action(u'resource_view_delete')(context, {
                u'id': res_view_dict[u'id'],
                u'resource_id': res_dict[u'id']
                })

        with nose.tools.assert_raises(toolkit.NotAuthorized):
            self._make_resource_view(res_dict[u'id'], user='test_member_2')
