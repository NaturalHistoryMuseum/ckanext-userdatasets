import importlib
from ckan.plugins import toolkit


def get_default_auth(ftype, function_name):
    '''Return the default auth function

    :param type: The type of auth function (create/update/delete)
    :param function: Name of function. It must exist.
    :param ftype:
    :param function_name:
    :returns: The auth function

    '''
    default_module = importlib.import_module(
        toolkit.config[u'default_auth_module'] + u'.' + ftype)
    return getattr(default_module, function_name)


def get_default_action(ftype, function_name):
    '''Return the default action function

    :param type: The type of action function (create/update/get)
    :param function: Name of function. It must exist.
    :param ftype:
    :param function_name:
    :returns: The action function

    '''
    default_module = importlib.import_module(
        toolkit.config[u'default_action_module'] + u'.' + ftype)
    return getattr(default_module, function_name)