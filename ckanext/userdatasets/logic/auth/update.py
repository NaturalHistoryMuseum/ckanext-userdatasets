from ckan.logic.auth import get_package_object, get_resource_object
from ckanext.userdatasets.logic.auth.auth import user_owns_package_as_member, user_is_member_of_package_org
from ckanext.userdatasets.logic.auth.auth import get_resource_view_object

def package_update(fb, context, data_dict):
    user = context['auth_user_obj']
    package = get_package_object(context, data_dict)
    if user_owns_package_as_member(user, package):
        return {'success': True}

    return fb(context, data_dict)

def resource_update(fb, context, data_dict):
    user = context['auth_user_obj']
    resource = get_resource_object(context, data_dict)
    package = resource.resource_group.package
    if user_owns_package_as_member(user, package):
        return {'success': True}
    elif user_is_member_of_package_org(user, package):
        return {'success': False}

    return fb(context, data_dict)

def resource_view_update(fb, context, data_dict):
    user = context['auth_user_obj']
    resource_view = get_resource_view_object(context, data_dict)
    resource = get_resource_object(context, {'id': resource_view.resource_id})
    if user_owns_package_as_member(user, resource.resource_group.package):
        return {'success': True}
    elif user_is_member_of_package_org(user, resource.resource_group.package):
        return {'success': False}

    return fb(context, data_dict)
