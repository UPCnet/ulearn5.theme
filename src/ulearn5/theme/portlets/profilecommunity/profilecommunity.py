from hashlib import sha1
from copy import deepcopy
from plone import api
from Acquisition import aq_inner
from Acquisition import aq_chain
from OFS.Image import Image
from zope.interface import implements
from zope.component import queryUtility
from zope.component import getMultiAdapter

from plone.app.portlets.portlets import base
from plone.registry.interfaces import IRegistry
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ulearn5.core.badges import AVAILABLE_BADGES
from ulearn5.core.content.community import ICommunity
from ulearn5.core.controlpanel import IUlearnControlPanelSettings

from base5.core.utils import get_safe_member_by_id, pref_lang


class IProfileCommunityPortlet(IPortletDataProvider):
    """ A portlet which can render the community information. """


class Assignment(base.Assignment):
    implements(IProfileCommunityPortlet)

    title = _(u'profilecommunity', default=u'Profile Community')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('profilecommunity.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.username = api.user.get_current().id
        self.user_info = get_safe_member_by_id(self.username)
        self.portal_url = api.portal.get().absolute_url()

    def has_webmaster_role(self):
        return 'WebMaster' in api.user.get_roles()

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

    def showEditCommunity(self):
        if not IPloneSiteRoot.providedBy(self.context) and \
           ICommunity.providedBy(self.context) and \
           'Owner' in api.user.get_roles(username=self.username, obj=self.context):
            return True

    def get_addable_types(self):
        factories_view = getMultiAdapter((self.context, self.request), name='folder_factories')
        return factories_view.addable_types()

    def get_posts_literal(self):
        literal = api.portal.get_registry_record(name='ulearn5.core.controlpanel.IUlearnControlPanelSettings.people_literal')
        if literal == 'thinnkers':
            return 'thinnkins'
        else:
            return 'entrades'

    def get_hash(self, community):
        return sha1(community.absolute_url()).hexdigest()

    def isCurrentPage(self, page):
        param = False
        path = self.context.absolute_url_path()
        if page in path:
            param = True
        return param

    def get_community_type(self, community):
        return community.community_type


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
