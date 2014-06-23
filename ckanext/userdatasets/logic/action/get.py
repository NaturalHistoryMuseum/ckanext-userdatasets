from ckanext.userdatasets.plugin import get_default_action


def organization_list_for_user(context, data_dict):
    perm = data_dict.get('permission')
    if perm in ['create_dataset', 'update_dataset', 'delete_dataset']:
        # Create a copy of the data dict, and change the request permission to
        # 'read' which will be granted to all members of a group.
        data_dict = dict(data_dict.items() + {'permission': 'read'}.items())

    fallback = get_default_action('get', 'organization_list_for_user')
    return fallback(context, data_dict)
