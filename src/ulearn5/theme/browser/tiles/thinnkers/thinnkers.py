# -*- coding: utf-8 -*-
from hashlib import sha1
from plone import api
from Acquisition import aq_inner, aq_chain
from ulearn5.core.content.community import ICommunity
from base5.core.utils import get_safe_member_by_id, pref_lang
from ulearn5.core import _
from zope import schema
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile


class IThinnkers(Schema):
    """The tile display all people or community people"""

    tile_title = schema.TextLine(
        title=_(u"Thinnkers"),
        description=_(u"Title of thinnkers"),
        default=(u"Thinnkers"),
        required=True)


class Thinnkers(Tile):
    """The tile display all people or community people"""

    def __call__(self):
        return self.index()

    def get_community(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return obj

    def community_mode(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True

        return False

    def get_people_literal(self):
        literal = api.portal.get_registry_record(name='ulearn5.core.controlpanel.IUlearnControlPanelSettings.people_literal')
        lang = pref_lang()

        if lang == 'ca' and literal == 'persones':
            literal = 'Persones'
        elif lang == 'es' and literal == 'persones':
            literal = 'Personas'
        elif lang == 'en' and literal == 'persones':
            literal = 'People'

        if lang == 'ca' and literal == 'participants':
            literal = 'Participants'
        elif lang == 'es' and literal == 'participants':
            literal = 'Participantes'
        elif lang == 'en' and literal == 'participants':
            literal = 'Participants'

        if literal == 'thinnkers':
            literal = 'Thinnkers'

        return literal

    def get_seemoreusers_literal(self):
        return 'seemoreusers_{}'.format(self.get_people_literal())

    def get_hash(self, community):
        return sha1(community.absolute_url()).hexdigest()


    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('tile_title', '')
