#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-userdatasets
# Created by the Natural History Museum in London, UK

import logging
import datetime
import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.lib.dictization.model_save as model_save

from ckan.logic import check_access, get_action, ValidationError, NotFound
from ckan.common import _

from ckan.logic.validators import owner_org_validator as default_oov
from ckanext.userdatasets.logic.validators import owner_org_validator as uds_oov

log = logging.getLogger(__name__)

def package_update(context, data_dict):
    '''

    :param context: 
    :param data_dict: 

    '''
    model = context[u'model']
    user = context[u'user']
    name_or_id = data_dict.get(u'id') or data_dict[u'name']

    pkg = model.Package.get(name_or_id)
    if pkg is None:
        raise NotFound(_(u'Package was not found.'))
    context[u'package'] = pkg
    data_dict[u'id'] = pkg.id

    check_access(u'package_update', context, data_dict)

    # get the schema
    package_plugin = lib_plugins.lookup_package_plugin(pkg.type)
    if u'schema' in context:
        schema = context[u'schema']
    else:
        schema = package_plugin.update_package_schema()
    # We modify the schema here to replace owner_org_validator by our own
    if u'owner_org' in schema:
        schema[u'owner_org'] = [uds_oov if f is default_oov else f for f in schema[u'owner_org']]

    if u'api_version' not in context:
        # check_data_dict() is deprecated. If the package_plugin has a
        # check_data_dict() we'll call it, if it doesn't have the method we'll
        # do nothing.
        check_data_dict = getattr(package_plugin, u'check_data_dict', None)
        if check_data_dict:
            try:
                package_plugin.check_data_dict(data_dict, schema)
            except TypeError:
                # Old plugins do not support passing the schema so we need
                # to ensure they still work.
                package_plugin.check_data_dict(data_dict)

    data, errors = lib_plugins.plugin_validate(
        package_plugin, context, data_dict, schema, u'package_update')
    log.debug(u'package_update validate_errs=%r user=%s package=%s data=%r',
              errors, context.get(u'user'),
              context.get(u'package').name if context.get(u'package') else u'',
              data)

    if errors:
        model.Session.rollback()
        raise ValidationError(errors)

    rev = model.repo.new_revision()
    rev.author = user
    if u'message' in context:
        rev.message = context[u'message']
    else:
        rev.message = _(u'REST API: Update object %s') % data.get(u'name')

    #avoid revisioning by updating directly
    model.Session.query(model.Package).filter_by(id=pkg.id).update(
        {u'metadata_modified': datetime.datetime.utcnow()})
    model.Session.refresh(pkg)

    pkg = model_save.package_dict_save(data, context)

    context_org_update = context.copy()
    context_org_update[u'ignore_auth'] = True
    context_org_update[u'defer_commit'] = True
    get_action(u'package_owner_org_update')(context_org_update,
                                            {u'id': pkg.id,
                                             u'organization_id': pkg.owner_org})

    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.edit(pkg)

        item.after_update(context, data)

    if not context.get(u'defer_commit'):
        model.repo.commit()

    log.debug(u'Updated object %s' % pkg.name)

    return_id_only = context.get(u'return_id_only', False)

    # Make sure that a user provided schema is not used on package_show
    context.pop(u'schema', None)

    # we could update the dataset so we should still be able to read it.
    context[u'ignore_auth'] = True
    output = data_dict[u'id'] if return_id_only \
            else get_action(u'package_show')(context, {u'id': data_dict[u'id']})

    return output
