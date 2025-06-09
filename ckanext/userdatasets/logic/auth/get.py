#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

from ckan.logic.auth import get_package_object
from ckan.plugins import toolkit
from ckantools.decorators import auth

from ckanext.userdatasets.logic.auth.auth import (
    user_owns_package_as_member,
)


@auth()
@toolkit.chained_auth_function
def package_collaborator_list(next_auth, context, data_dict):
    user = context['auth_user_obj']

    package_id = data_dict.get('id')
    package = get_package_object(context, {'id': package_id})
    if user_owns_package_as_member(user, package):
        return {'success': True}

    return next_auth(context, data_dict)
