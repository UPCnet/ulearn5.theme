# -*- coding: utf-8 -*-
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from zope import schema
from ulearn5.core.utils import is_activate_sharedwithme, is_activate_news



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

    def getClass(self):
        """ Returns class for links """
        shared = is_activate_sharedwithme()
        news = is_activate_news()
        width = ''
        if shared and news:
            width = 'col-md-3'
        elif shared and not news:
            width = 'col-md-4'
        elif news and not shared:
            width = 'col-md-4'
        else:
            width = 'col-md-6'

        return "active bubble top " + width

    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('tile_title', '')
