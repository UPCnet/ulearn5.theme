# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from plone.memoize.instance import memoize
from zope import schema
from Products.CMFCore.utils import getToolByName
from base5.core.utils import pref_lang


class IHomeButtonBar(Schema):
    """A banner which can render element tagged with premsa-destacat-agenda"""

    tile_title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Title of the tile"),
        default=u'Button bar',
        required=True)


class HomeButtonBar(Tile):
    """The Banner tile displays an element tagged with premsa-destacat-agenda"""

    def __call__(self):
        return self.index()


    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('tile_title', '')
