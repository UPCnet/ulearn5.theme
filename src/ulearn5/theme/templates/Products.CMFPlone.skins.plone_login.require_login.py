## Script (Python) "require_login"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Login

login = 'login'

portal = context.portal_url.getPortalObject()
# if cookie crumbler did a traverse instead of a redirect,
# this would be the way to get the value of came_from
#url = portal.getCurrentUrl()
#context.REQUEST.set('came_from', url)
from DateTime import DateTime

# Descomentar para poder debuggar. Como no se puede poner ipdb con loggers
# import logging
# logger = logging.getLogger('azure')
# try:
#    import urllib
# except Exception as e:
#    logger.error('YYY ERROR IMPORT REQUEST {}'.format(str(e)))
#    pass

if context.portal_membership.isAnonymousUser():
    if 'acl_msal' in portal.acl_users:
       acl_msal = portal.acl_users['acl_msal']
       portal_url = context.portal_url()
       portal_url_came_from = context.REQUEST.get('came_from', portal_url)
       zope_DT = DateTime()
       uuid = ''.join([a for a in str(zope_DT) if a.isalnum()])
       url_azure = acl_msal.AUTHORITY + '/oauth2/v2.0/authorize?scope=' + str(''.join(acl_msal.SCOPE)) + '+offline_access+openid+profile&state=' + str(uuid) + '|' + portal_url_came_from + '&redirect_uri=' + portal_url + acl_msal.REDIRECT_PATH + '&response_type=code&client_id=' + acl_msal.CLIENT_ID
       context.REQUEST.response.redirect(url_azure)
    else:
       return portal.restrictedTraverse(login)()
else:
    from AccessControl import getSecurityManager
    if getSecurityManager().checkPermission("zope2.View", context):
        came_from = context.REQUEST.get('came_from')
        if came_from:
            context.REQUEST.response.redirect(came_from)
        else:
            return portal.restrictedTraverse('insufficient_privileges')()
    else:
        return portal.restrictedTraverse('insufficient_privileges')()