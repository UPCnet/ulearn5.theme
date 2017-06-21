from zope.interface import implements
from plone import api
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _


class ISharedWithMePortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(ISharedWithMePortlet)

    title = _(u'sharedwithme', default=u'SharedWithMe')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/sharedwithme.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.portal_url = api.portal.get().absolute_url()


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
