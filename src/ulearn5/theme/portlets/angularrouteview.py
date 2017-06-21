from plone import api
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


class IAngularRouteViewPortlet(IPortletDataProvider):
    """ A portlet angular route view """


class Assignment(base.Assignment):
    implements(IAngularRouteViewPortlet)

    title = _(u'angularrouteview', default=u'AngularRouteView')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/angularrouteview.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.portal_url = api.portal.get().absolute_url()

    def is_siteroot(self):
        if IPloneSiteRoot.providedBy(self.context):
            return None
        else:
            return ''


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
