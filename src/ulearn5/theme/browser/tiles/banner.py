# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from plone.memoize.instance import memoize
from zope import schema
from Products.CMFCore.utils import getToolByName
from base5.core.utils import pref_lang


class IBanner(Schema):
    """A banner which can render element tagged with premsa-destacat-agenda"""

    tile_title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Title of the tile"),
        required=True)


class Banner(Tile):
    """The Banner tile displays an element tagged with premsa-destacat-agenda"""

    def __call__(self):
        return self.index()

    @memoize
    def getBanner(self):
        """ Returns a banner object """
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(review_state=['published'],
                          Language=pref_lang(),
                          sort_on=('effective'),
                          sort_order='reverse',
                          sort_limit=1)
        banner = results[0].getObject() if len(results) > 0 else None
        return banner

    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('tile_title', '')

