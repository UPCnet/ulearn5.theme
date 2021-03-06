# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from hashlib import sha1
from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements

from base5.core.utils import get_safe_member_by_id
from base5.core.utils import pref_lang
from ulearn5.core import _
from ulearn5.core.content.community import ICommunity


class IThinnkersPortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(IThinnkersPortlet)

    title = _(u'thinnkers portlet')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/thinnkers.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.username = api.user.get_current().id
        self.user_info = get_safe_member_by_id(self.username)
        self.portal_url = api.portal.get().absolute_url()

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

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


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
