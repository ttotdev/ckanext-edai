# encoding: utf-8

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

def group_create(context, data_dict=None):
    # Get the user name of the logged-in user.
    user_name = context['user']

    # Get a list of the members of the 'curators' group.
    try:
        members = toolkit.get_action('member_list')(
            data_dict={'id': 'curators', 'object_type': 'user'})
    except toolkit.ObjectNotFound:
        # The curators group doesn't exist.
        return {'success': False,
                'msg': "The curators groups doesn't exist, so only sysadmins "
                       "are authorized to create groups."}

    # 'members' is a list of (user_id, object_type, capacity) tuples, we're
    # only interested in the user_ids.
    member_ids = [member_tuple[0] for member_tuple in members]

    # We have the logged-in user's user name, get their user id.
    convert_user_name_or_id_to_id = toolkit.get_converter(
        'convert_user_name_or_id_to_id')
    try:
        user_id = convert_user_name_or_id_to_id(user_name, context)
    except toolkit.Invalid:
        # The user doesn't exist (e.g. they're not logged-in).
        return {'success': False,
                'msg': 'You must be logged-in as a member of the curators '
                       'group to create new groups.'}

    # Finally, we can test whether the user is a member of the curators group.
    if user_id in member_ids:
        return {'success': True}
    else:
        return {'success': False,
                'msg': 'Only curators are allowed to create groups'}


class EdaiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurer)	

    def get_auth_functions(self):
        return {'group_create': group_create}


    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        toolkit.add_template_directory(config, 'templates')

        # Add this plugin's public dir to CKAN's extra_public_paths, so
        # that CKAN will use this plugin's custom static files.
        toolkit.add_public_directory(config, 'public')

        # Register this plugin's fanstatic directory with CKAN.
        # Here, 'fanstatic' is the path to the fanstatic directory
        # (relative to this plugin.py file), and 'example_theme' is the name
        # that we'll use to refer to this fanstatic directory from CKAN
        # templates.
        toolkit.add_resource('fanstatic', 'edai_theme')
