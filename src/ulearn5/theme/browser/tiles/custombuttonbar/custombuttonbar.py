# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from plone.memoize.instance import memoize
from zope import schema
from Products.CMFCore.utils import getToolByName
from base5.core.utils import pref_lang

from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite

class ICustomButtonBar(Schema):
    """A banner which can render element tagged with premsa-destacat-agenda"""

    tile_title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Title of the tile"),
        default=(u"Custom button bar"),
        required=True)


class CustomButtonBar(Tile):
    """The Banner tile displays an element tagged with premsa-destacat-agenda"""

    def __call__(self):
        return self.index()

    def portal_url(self):
        return self.portal().absolute_url()

    def portal(self):
        return getSite()

    def pref_lang(self):
        """ Extracts the current language for the current user
        """
        lt = getToolByName(self.portal(), 'portal_languages')
        return lt.getPreferredLanguage()

    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('tile_title', '')
