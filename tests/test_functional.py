#!/usr/bin/env python3
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
        kwargs['owner_org'] = org['id']

    if user is not None:
        kwargs['user'] = user

    return factories.Dataset(**kwargs)


@pytest.fixture
def org():
    return factories.Organization()


@pytest.fixture
def member_1(org):
    user = factories.User(name='test_member_1')
    call_action(
        'organization_member_create', id=org['id'], username=user['name'], role='member'
    )
    return user


@pytest.fixture
def member_2(org):
    user = factories.User(name='test_member_2')
    call_action(
        'organization_member_create', id=org['id'], username=user['name'], role='member'
    )
    return user


@pytest.fixture
def editor(org):
    user = factories.User(name='test_editor')
    call_action(
        'organization_member_create', id=org['id'], username=user['name'], role='editor'
    )
    return user


@pytest.mark.ckan_config('ckan.plugins', 'userdatasets')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
class TestFuncDatasets(object):
    def test_members_can_edit_own_datasets(self, org, member_1):
        """
        Tests datasets.
        """
        package = create_package(org, member_1)
        context = {'user': member_1['name']}
        package = toolkit.get_action('package_update')(
            context,
            {
                'id': package['id'],
                'title': 'title for test_members_can_edit_own_datasets',
            },
        )
        assert package['title'] == 'title for test_members_can_edit_own_datasets'

    def test_editors_can_edit_org_datasets(self, org, member_1, editor):
        package = create_package(org, member_1)
        context = {'user': editor['name']}
        package = toolkit.get_action('package_update')(
            context,
            {
                'id': package['id'],
                'title': 'title for test_editors_can_edit_org_datasets',
            },
        )
        assert package['title'] == 'title for test_editors_can_edit_org_datasets'

    def test_members_cannot_edit_others_datasets(self, org, member_1, member_2):
        package = create_package(org, member_1)
        # Attempt to update test_pkg_1 as member test_member_2
        with pytest.raises(toolkit.NotAuthorized, match=member_2['name']):
            context = {'user': member_2['name']}
            toolkit.get_action('package_update')(
                context,
                {
                    'id': package['id'],
                    'title': 'title for test_members_cannot_edit_others_datasets',
                },
            )

        # Attempt to delete test_pkg_1 as member test_member_2
        with pytest.raises(toolkit.NotAuthorized, match=member_2['name']):
            context = {'user': member_2['name']}
            toolkit.get_action('package_delete')(context, {'id': package['id']})

    def test_non_members_cannot_create_datasets(self, member_1):
        with pytest.raises(toolkit.NotAuthorized, match=member_1['name']):
            another_org = factories.Organization()
            toolkit.get_action('package_create')(
                {'user': member_1['name']}, {'owner_org': another_org['id']}
            )


@pytest.mark.ckan_config('ckan.plugins', 'userdatasets')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
class TestFuncResources(object):
    def test_members_can_edit_own_resources(self, org, member_1):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package['id'])

        context = {'user': member_1['name']}
        resource = toolkit.get_action('resource_update')(
            context, {'id': resource['id'], 'description': 'test description 2'}
        )
        assert resource['description'] == 'test description 2'

    def test_editors_can_edit_org_resources(self, org, member_1, editor):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package['id'])

        context = {'user': editor['name']}
        resource = toolkit.get_action('resource_update')(
            context,
            {'id': resource['id'], 'description': 'test description for test_editor'},
        )
        assert resource['description'] == 'test description for test_editor'

    def test_members_cannot_edit_others_resources(self, org, member_1, member_2):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package['id'])

        context = {'user': member_2['name']}

        with pytest.raises(toolkit.NotAuthorized):
            resource = toolkit.get_action('resource_update')(
                context, {'id': resource['id'], 'description': 'this should not work'}
            )

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action('resource_delete')(context, {'id': resource['id']})

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action('resource_create')(
                context, {'package_id': package['id'], 'description': 'beans!'}
            )


# the ResourceView factory requires the use of the image_view plugin for default functionality
@pytest.mark.ckan_config('ckan.plugins', 'userdatasets image_view')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
class TestFuncResourceViews(object):
    def test_members_can_edit_own_resource_views(self, org, member_1):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package['id'])
        resource_view = factories.ResourceView(resource_id=resource['id'])

        context = {'user': member_1['name']}
        new_desc = 'description for test_members_can_edit_own_resource_views'
        resource_view_updated = toolkit.get_action('resource_view_update')(
            context,
            {
                'id': resource_view['id'],
                'resource_id': resource['id'],
                'description': new_desc,
            },
        )
        assert resource_view_updated['description'] == new_desc
        assert resource_view['description'] != resource_view_updated['description']

    def test_editors_can_edit_org_resource_views(self, org, member_1, editor):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package['id'])
        resource_view = factories.ResourceView(resource_id=resource['id'])

        context = {'user': editor['name']}
        new_desc = 'description for test_editors_can_edit_org_resource_views'
        resource_view_updated = toolkit.get_action('resource_view_update')(
            context,
            {
                'id': resource_view['id'],
                'resource_id': resource['id'],
                'description': new_desc,
            },
        )
        assert resource_view_updated['description'] == new_desc
        assert resource_view['description'] != resource_view_updated['description']

    def test_members_cannot_edit_others_resource_views(self, org, member_1, member_2):
        package = create_package(org, member_1)
        resource = factories.Resource(package_id=package['id'])
        resource_view = factories.ResourceView(resource_id=resource['id'])

        context = {'user': member_2['name']}
        new_desc = 'description for test_members_cannot_edit_others_resource_views'

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action('resource_view_update')(
                context,
                {
                    'id': resource_view['id'],
                    'resource_id': resource['id'],
                    'description': new_desc,
                },
            )

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action('resource_view_delete')(
                context, {'id': resource_view['id'], 'resource_id': resource['id']}
            )

        with pytest.raises(toolkit.NotAuthorized):
            toolkit.get_action('resource_view_create')(
                context,
                {
                    'resource_id': resource['id'],
                    'title': 'beans!',
                    'view_type': 'image_view',
                },
            )
