from ckan.new_authz import users_role_for_group_or_org

def user_owns_package_as_member(user, package):
    """Checks that the given user created the package, and has the 'member' role in the organization that owns the package.

    @param user: A user object
    @param package: A package object
    @return: True if the user created the package and has the 'member' role in the organization to which package belongs.
             False otherwise.
    """
    if user.id == package.creator_user_id and package.owner_org:
        role_in_org = users_role_for_group_or_org(package.owner_org, user.name)
        if role_in_org == 'member':
            return True
    return False
