from ckan.logic.auth import get_package_object
from ckan.new_authz import users_role_for_group_or_org, has_user_permission_for_some_org
from ckanext.userdatasets.logic.auth.auth import user_owns_package_as_member

def package_create(fb, context, data_dict):
    user = context['auth_user_obj']
    if data_dict and 'owner_org' in data_dict:
        role = users_role_for_group_or_org(data_dict['owner_org'], user.name)
        if role == 'member':
            return {'success': True}
    else:
        # If there is no organization, then this should return success if the user can create datasets for *some*
        # organisation (see the ckan implementation), so either if anonymous packages are allowed or if we have
        # member status in any organization.
        if has_user_permission_for_some_org(user.name, 'read'):
            return {'success': True}

    return fb(context, data_dict)

def resource_create(fb, context, data_dict):
    user = context['auth_user_obj']
    package = get_package_object(context, data_dict)
    if user_owns_package_as_member(user, package):
        return {'success': True}

    return fb(context, data_dict)

def resource_view_create(fb, context, data_dict):
    user = context['auth_user_obj']
    package = get_package_object(context, data_dict)
    if user_owns_package_as_member(user, package):
        return {'success': True}

    return fb(context, data_dict)

