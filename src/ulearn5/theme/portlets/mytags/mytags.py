# -*- coding: utf-8 -*-
from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ulearn5.core import _
from ulearn5.core.controlpanel import IUlearnControlPanelSettings
from ulearn5.core.utils import get_or_initialize_annotation
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import implementer


class IMyTagsPortlet(IPortletDataProvider):
    """A portlet which can show actived."""


@implementer(IMyTagsPortlet)
class Assignment(base.Assignment):

    title = _("mytags", default="My Tags")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile("mytags.pt")

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def getMyTags(self):
        current_user = api.user.get_current()
        userid = current_user.id

        user_subscribed_tags = get_or_initialize_annotation('user_subscribed_tags')
        record = next((r for r in user_subscribed_tags.values() if r.get('id') == userid), {})

        return record.get('tags', [])


    def getPrimaryColor(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings)
        return settings.main_color


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
