from AccessControl import getSecurityManager
from DateTime import DateTime
from six.moves.urllib import parse
from zope.component import getMultiAdapter


def require_login_call(self):
    url = ''
    portal_state = getMultiAdapter(
        (self.context, self.request),
        name='plone_portal_state',
    )
    portal = portal_state.portal()
    
    if portal_state.anonymous():

        if 'acl_msal' in portal.acl_users:
            acl_msal = portal.acl_users['acl_msal']
            portal_url = self.context.portal_url()
            portal_url_came_from = self.context.REQUEST.get('came_from', portal_url)
            zope_DT = DateTime()
            uuid = ''.join([a for a in str(zope_DT) if a.isalnum()])
            url_azure = acl_msal.AUTHORITY + '/oauth2/v2.0/authorize?scope=' + str(''.join(acl_msal.SCOPE)) + '+offline_access+openid+profile&state=' + str(uuid) + '|' + portal_url_came_from + '&redirect_uri=' + portal_url + acl_msal.REDIRECT_PATH + '&response_type=code&client_id=' + acl_msal.CLIENT_ID
            url = url_azure
        else:
            url = f'{portal.absolute_url()}/login'
            came_from = self.request.get('came_from', None)
            if came_from:
                url += f'?came_from={parse.quote(came_from)}'

    else:

        if getSecurityManager().checkPermission("zope2.View", self.context):
            came_from = self.context.REQUEST.get('came_from')
            if came_from:
                url  = came_from
            else: 
                url = f'{portal.absolute_url()}/insufficient-privileges'
        else:
            url = f'{portal.absolute_url()}/insufficient-privileges'
        
    self.request.response.redirect(url)