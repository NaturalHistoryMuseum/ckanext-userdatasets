from ckan.logic.auth import get_package_object, get_resource_object
from ckanext.userdatasets.logic.auth.auth import user_owns_package_as_member

def package_delete(fb, context, data_dict):
    user = context['auth_user_obj']
    package = get_package_object(context, data_dict)

    if user_owns_package_as_member(user, package):
        return {'success': True}

    return fb(context, data_dict)

def resource_delete(fb, context, data_dict):
    user = context['auth_user_obj']
    resource = get_resource_object(context, data_dict)
    package = resource.resource_group.package
    if user_owns_package_as_member(user, package):
        return {'success': True}

    return fb(context, data_dict)

def resource_view_delete(fb, context, data_dict):
    user = context['auth_user_obj']
    package = get_package_object(context, data_dict)
    if user_owns_package_as_member(user, package):
        return {'success': True}

    return fb(context, data_dict)

