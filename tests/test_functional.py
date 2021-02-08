#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK
import pytest
from ckan.plugins import toolkit
from ckan.tests import factories
from ckan.tests.helpers import call_action


def create_package(org=None, user=None):
    kwargs = {}
    if org is not None:
        kwargs[u'owner_org'] = org[u'id']

    if user is not None:
        kwargs[u'user'] = user

    return factories.Dataset(**kwargs)


@pytest.fixture
def org():
    return factories.Organization()


@pytest.fixture
def member_1(org):
    user = factories.User(name=u'test_member_1')
    call_action(u'organization_member_create', id=org[u'id'], username=user[u'name'],
                role=u'member')
    return user


@pytest.fixture
def member_2(org):
    user = factories.User(name=u'test_member_2')
    call_action(u'organization_member_create', id=org[u'id'], username=user[u'name'],
                role=u'member')
    return user


@pytest.fixture
def editor(org):
    user = factories.User(name=u'test_editor')
    call_action(u'organization_member_create', id=org[u'id'], username=user[u'name'],
                role=u'editor')
    return user


@pytest.mark.ckan_config(u'ckan.plugins', u'userdatasets')
@pytest.mark.usefixtures(u'clean_db', u'with_plugins', u'with_request_context')
class TestFuncDatasets(object):

    def test_members_can_edit_own_datasets(self, org, member_1):
        '''Tests datasets'''
        package = create_package(org, member_1)
        context = {u'user': member_1[u'name']}
        package = toolkit.get_action(u'package_update')(context, {
            u'id': package[u'id'],
            u'title': u'title for test_members_can_edit_own_datasets'
        })
        assert package[u'title'] == u'title for test_members_can_edit_own_datasets'

    def test_editors_can_edit_org_datasets(self, org, member_1, editor):
        package = create_package(org, member_1)
        context = {u'user': editor[u'name']}
        package = toolkit.get_action(u'package_update')(context, {
            u'id': package[u'id'],
            u'title': u'title for test_editors_can_edit_org_datasets'
        })
        assert package[u'title'] == u'title for test_editors_can_edit_org_datasets'

    def test_members_cannot_edit_others_datasets(self, org, member_1, member_2):
        package = create_package(org, member_1)
        # Attempt to update test_pkg_1 as member test_member_2
        with pytest.raises(toolkit.NotAuthorized, match=member_2[u'name']):
            context = {u'user': member_2[u'name']}
            toolkit.get_action(u'package_update')(context, {
                u'id': package[u'id'],
                u'title': u'title for test_members_cannot_edit_others_datasets'
            })

        # Attempt to delete test_pkg_1 as member test_member_2
        with pytest.raises(toolkit.NotAuthorized, match=member_2[u'name']):
            context = {u'user': member_2[u'name']}
            toolkit.get_action(u'package_delete')(context, {
                u'id': package[u'id']
            })

    def test_non_members_cannot_create_datasets(self, member_1):
        with pytest.raises(toolkit.NotAuthorized, match=member_1[u'name']):
            another_org = factories.Organization()
            toolkit.get_action(u'package_create')({u'user': member_1[u'name']},
                                                  {u'owner_org': another_org[u'id']})


@pytest.mark.ckan_config(u'ckan.plugins', u'userdatasets')
@pytest.mark.usefixtures(u'clean_db', u'with_plugins', u'with_request_context')
class TestFuncResources(object):

    def test_members_can_edit_own_resources(self, org, member_1):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package[u'id'])

        context = {u'user': member_1[u'name']}
        resource = toolkit.get_action(u'resource_update')(context, {
            u'id': resource[u'id'],
            u'description': u'test description 2'
        })
        assert resource[u'description'] == u'test description 2'

    def test_editors_can_edit_org_resources(self, org, member_1, editor):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package[u'id'])

        context = {u'user': editor[u'name']}
        resource = toolkit.get_action(u'resource_update')(context, {
            u'id': resource[u'id'],
            u'description': u'test description for test_editor'
        })
        assert resource[u'description'] == u'test description for test_editor'

    def test_members_cannot_edit_others_resources(self, org, member_1, member_2):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package[u'id'])

        context = {u'user': member_2[u'name']}

        with pytest.raises(toolkit.NotAuthorized):
            resource = toolkit.get_action(u'resource_update')(context, {
                u'id': resource[u'id'],
                u'description': u'this should not work'
            })

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action(u'resource_delete')(context, {u'id': resource[u'id']})

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action(u'resource_create')(context, {u'package_id': package[u'id'],
                                                             u'description': u'beans!'})


# the ResourceView factory requires the use of the image_view plugin for default functionality
@pytest.mark.ckan_config(u'ckan.plugins', u'userdatasets image_view')
@pytest.mark.usefixtures(u'clean_db', u'with_plugins', u'with_request_context')
class TestFuncResourceViews(object):

    def test_members_can_edit_own_resource_views(self, org, member_1):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package[u'id'])
        resource_view = factories.ResourceView(resource_id=resource[u'id'])

        context = {u'user': member_1[u'name']}
        new_desc = u'description for test_members_can_edit_own_resource_views'
        resource_view_updated = toolkit.get_action(u'resource_view_update')(context, {
            u'id': resource_view[u'id'],
            u'resource_id': resource[u'id'],
            u'description': new_desc
        })
        assert resource_view_updated[u'description'] == new_desc
        assert resource_view[u'description'] != resource_view_updated[u'description']

    def test_editors_can_edit_org_resource_views(self, org, member_1, editor):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package[u'id'])
        resource_view = factories.ResourceView(resource_id=resource[u'id'])

        context = {u'user': editor[u'name']}
        new_desc = u'description for test_editors_can_edit_org_resource_views'
        resource_view_updated = toolkit.get_action(u'resource_view_update')(context, {
            u'id': resource_view[u'id'],
            u'resource_id': resource[u'id'],
            u'description': new_desc
        })
        assert resource_view_updated[u'description'] == new_desc
        assert resource_view[u'description'] != resource_view_updated[u'description']

    def test_members_cannot_edit_others_resource_views(self, org, member_1, member_2):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package[u'id'])
        resource_view = factories.ResourceView(resource_id=resource[u'id'])

        context = {u'user': member_2[u'name']}
        new_desc = u'description for test_members_cannot_edit_others_resource_views'

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action(u'resource_view_update')(context, {
                u'id': resource_view[u'id'],
                u'resource_id': resource[u'id'],
                u'description': new_desc
            })

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action(u'resource_view_delete')(context, {
                u'id': resource_view[u'id'],
                u'resource_id': resource[u'id']
            })

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action(u'resource_view_create')(context, {
                u'resource_id': resource[u'id'],
                u'title': u'beans!',
                u'view_type': u'image_view'
            })
