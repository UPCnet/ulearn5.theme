# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from ulearn5.core.controlpanel import IUlearnControlPanelSettings

from plone.memoize.view import memoize_contextless
from zope.component.hooks import getSite
from souper.soup import get_soup
from repoze.catalog.query import Eq
from plone import api


class IMyTagsPortlet(IPortletDataProvider):
    """ A portlet which can show actived.
    """


class Assignment(base.Assignment):
    implements(IMyTagsPortlet)

    title = _(u'mytags', default=u'mytags')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('mytags.pt')

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    def getMyTags(self):
        portal = getSite()
        current_user = api.user.get_current()
        userid = current_user.id

        soup_tags = get_soup('user_subscribed_tags', portal)
        tags_soup = [r for r in soup_tags.query(Eq('id', userid))]

        return tags_soup[0].attrs['tags'] if tags_soup else []

    def getPrimaryColor(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings)
        return settings.main_color


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
