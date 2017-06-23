# -*- coding: utf-8 -*-
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from ulearn5.core.interfaces import IHomePage
from base5.core.utils import pref_lang


from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _
from zope.component.hooks import getSite


class ICustomButtonBarPortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(ICustomButtonBarPortlet)

    title = _(u'custombuttonbar', default=u'Custom button bar')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('custombuttonbar.pt')

    def getHomepage(self):
        page = {}
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                  Language=pref_lang())
        page['body'] = result[0].CookedBody()

        return page

    def portal_url(self):
        return self.portal().absolute_url()

    def portal(self):
        return getSite()

    def pref_lang(self):
        """ Extracts the current language for the current user
        """
        lt = getToolByName(self.portal(), 'portal_languages')
        return lt.getPreferredLanguage()


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
