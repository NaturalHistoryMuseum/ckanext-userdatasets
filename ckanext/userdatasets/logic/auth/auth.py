from ckan import logic
from ckan.new_authz import users_role_for_group_or_org

def user_is_member_of_package_org(user, package):
    """Return True if the package is in an organization and the user has the member role in that organization

    @param user: A user object
    @param package: A package object
    @return: True if the user has the 'member' role in the organization that owns the package, False otherwise
    """
    if package.owner_org:
        role_in_org = users_role_for_group_or_org(package.owner_org, user.name)
        if role_in_org == 'member':
            return True
    return False

def user_owns_package_as_member(user, package):
    """Checks that the given user created the package, and has the 'member' role in the organization that owns the package.

    @param user: A user object
    @param package: A package object
    @return: True if the user created the package and has the 'member' role in the organization to which package belongs.
             False otherwise.
    """
    if user_is_member_of_package_org(user, package):
        return package.creator_user_id and user.id == package.creator_user_id

    return False

def get_resource_view_object(context, data_dict):
    """Return the resource view object present either (as an object) in the context, or in the data dict (as 'id')"""
    try:
        return context['resource_view']
    except KeyError:
        model = context['model']
        if not data_dict:
            data_dict = {}
        id = data_dict.get('id', None)
        if not id:
            raise logic.ValidationError('Missing id, can not get {0} object'
                                        .format('ResourceView'))
        obj = getattr(model, 'ResourceView').get(id)
        if not obj:
            raise logic.NotFound
        # Save in case we need this again during the request
        context['resource_view'] = obj
        return obj