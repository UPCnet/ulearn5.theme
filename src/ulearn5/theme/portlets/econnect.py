from zope.interface import implements
from zope.component.hooks import getSite
from zope.security import checkPermission

from plone.app.portlets.portlets import base
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IeConnectPortlet(IPortletDataProvider):
    """ A portlet which can render the econnect tools """


class Assignment(base.Assignment):
    implements(IeConnectPortlet)

    title = _(u'Meetings space', default=u'Meetings space')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/econnect.pt')

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def allow_render(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        user = pm.getAuthenticatedMember()

        return 'WebMaster' in user.getRoles()


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
