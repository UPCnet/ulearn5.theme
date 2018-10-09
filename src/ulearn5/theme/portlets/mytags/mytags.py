# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from repoze.catalog.query import Eq
from souper.soup import get_soup
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import implements

from ulearn5.core import _
from ulearn5.core.controlpanel import IUlearnControlPanelSettings


class IMyTagsPortlet(IPortletDataProvider):
    """ A portlet which can show actived.
    """


class Assignment(base.Assignment):
    implements(IMyTagsPortlet)

    title = _(u'mytags', default=u'My Tags')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('mytags.pt')

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

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
