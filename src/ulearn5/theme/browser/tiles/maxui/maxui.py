# -*- coding: utf-8 -*-
from ulearn5.core import _
from zope import schema
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from plone.memoize.view import memoize_contextless
from zope.component.hooks import getSite


class IMaxUI(Schema):
    """The tile display Max UI"""

    tile_title = schema.TextLine(
        title=_(u"Max UI"),
        description=_(u"Title of Max UI"),
        default=(u"Max UI"),
        required=True)


class MaxUI(Tile):
    """The tile display Max UI"""

    def __call__(self):
        return self.index()

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()


    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('tile_title', '')
