"""
Install WebServerAuth into or uninstall from a given portal.
"""

from Products.CMFCore.utils import getToolByName

from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin

from Products.WebServerAuth.plugin import MultiPlugin, implementedInterfaces
from Products.WebServerAuth.utils import firstIdOfClass
from Products.WebServerAuth import zmi


def install(context):
    """
    Install WebServerAuth into a given portal.
    """
    if context.readDataFile('WebServerAuth-install.txt') is None:
        return
    portal = context.getSite()

    acl_users = getToolByName(portal, 'acl_users')

    # Put a WebServerAuth multiplugin in the acl_users folder, if there isn't
    # one:
    id = firstIdOfClass(acl_users, MultiPlugin)
    if not id:
        id = 'web_server_auth'
        zmi.manage_addWebServerAuth(
            acl_users, id, title='WebServerAuth Plugin')

    # Activate it:
    plugins = acl_users['plugins']
    for interface in implementedInterfaces:
        plugins.activatePlugin(interface, id)  # plugins is a PluginRegistry

    # Make the Challenge plugin the first in the list:
    for i in range(list(plugins.listPluginIds(IChallengePlugin)).index(id)):
        plugins.movePluginsUp(IChallengePlugin, [id])

    # Set up login link:
    user_actions = getToolByName(portal, 'portal_actions')['user']
    user_actions['login']._updateProperty(
        'url_expr',
        "python:here.acl_users.web_server_auth.loginUrl(request.ACTUAL_URL)")


def uninstall(context):
    """
    Uninstall WebServerAuth from a given portal.
    """
    if context.readDataFile('WebServerAuth-uninstall.txt') is None:
        return
    portal = context.getSite()

    # Delete the multiplugin instance:
    acl_users = getToolByName(portal, 'acl_users')
    id = firstIdOfClass(acl_users, MultiPlugin)
    if id:
        acl_users.manage_delObjects(ids=[id])  # implicitly deactivates

    # Revert login link to its stock setting:
    user_actions = getToolByName(portal, 'portal_actions')['user']
    user_actions['login']._updateProperty(
        'url_expr', "string:${portal_url}/login_form")
