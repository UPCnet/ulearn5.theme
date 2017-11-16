# -*- coding: utf-8 -*-
import transaction
from plone import api
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from zope import schema



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

    def is_activate_sharedwithme(self):
        if (api.portal.get_registry_record('base5.core.controlpanel.core.IGenwebCoreControlPanelSettings.elasticsearch') != None) and (api.portal.get_registry_record('ulearn5.core.controlpanel.IUlearnControlPanelSettings.activate_sharedwithme') == True):
            portal = api.portal.get()
            if portal.portal_actions.object.local_roles.visible == False:
                portal.portal_actions.object.local_roles.visible = True
                transaction.commit()
            return True
        else:
            return False

    def is_activate_news(self):
        return api.portal.get_registry_record('ulearn5.core.controlpanel.IUlearnControlPanelSettings.activate_news')

    def getClass(self):
        """ Returns class for links """
        shared = self.is_activate_sharedwithme()
        news = self.is_activate_news()
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
