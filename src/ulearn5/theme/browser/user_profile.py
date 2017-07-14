from copy import deepcopy
from OFS.Image import Image

from zope.interface import implements
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.component import getUtilitiesFor

from plone.memoize.view import memoize_contextless
from plone.registry.interfaces import IRegistry

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from souper.interfaces import ICatalogFactory

from mrs5.max.utilities import IMAXClient
from ulearn5.core.badges import AVAILABLE_BADGES
from ulearn5.core.controlpanel import IUlearnControlPanelSettings
from base5.core.utils import get_safe_member_by_id
from ulearn5.core import _

from plone import api


class userProfile(BrowserView):
    """ Return an user profile ../profile/{username} """
    implements(IPublishTraverse)

    index = ViewPageTemplateFile('views_templates/user_profile.pt')

    def __init__(self, context, request):
        super(userProfile, self).__init__(context, request)
        self.username = None
        self.portal = api.portal.get()
        self.portal_url = self.portal.absolute_url()

    def __call__(self):
        return self.index()

    def publishTraverse(self, request, name):
        if self.username is None:  # ../profile/username
            self.username = name
            self.user_info = api.user.get(self.username)
            member_info = get_safe_member_by_id(self.user_info.id)
            self.user_fullname = member_info.get('fullname', '')
        else:
            raise NotFound(self, name, request)
        return self

    def get_posts_literal(self):
        literal = api.portal.get_registry_record(name='ulearn.core.controlpanel.IUlearnControlPanelSettings.people_literal')
        if literal == 'thinnkers':
            return 'thinnkins'
        else:
            return 'entrades'

    def has_complete_profile(self):
        if self.user_info:
            pm = api.portal.get_tool('portal_membership')
            portrait = pm.getPersonalPortrait(self.user_info.id)
            member_info = get_safe_member_by_id(self.user_info.id)

            if member_info.get('fullname', False) \
               and member_info.get('fullname', False) != self.username \
               and member_info.get('email', False) \
               and isinstance(portrait, Image):
                return True
            else:
                return False
        else:
            # The user doesn't have any property information for some weird
            # reason or simply beccause we are admin
            return False

    def get_user_info_for_display(self):
        user_properties_utility = getUtility(ICatalogFactory, name='user_properties')

        extender_name = api.portal.get_registry_record('base5.core.controlpanel.core.IGenwebCoreControlPanelSettings.user_properties_extender')

        rendered_properties = []
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            for prop in extended_user_properties_utility.profile_properties:
                rendered_properties.append(dict(
                    name=_(prop),
                    value=self.user_info.getProperty(prop, '')
                ))
            return rendered_properties
        else:
            # If it's not extended, then return the simple set of data we know
            # about the user using also the profile_properties field
            for prop in user_properties_utility.profile_properties:
                rendered_properties.append(dict(
                    name=_(prop),
                    value=self.user_info.getProperty(prop, '')
                ))
            return rendered_properties

    def get_member_data(self):
        return api.user.get_current()

    def user_properties(self):
        user_properties_default = [_(u'fullname'), _(u'email'), _(u'home_page'), _(u'description'), _(u'twitter_username'), _(u'location'), _(u'telefon'), _(u'ubicacio')]

        member_data = self.get_member_data()
        return {'fullname': member_data.getProperty('fullname'),
                'email': member_data.getProperty('email'),
                'home_page': member_data.getProperty('home_page'),
                'description': member_data.getProperty('description'),
                'twitter_username': member_data.getProperty('twitter_username'),
                'location': member_data.getProperty('location'),
                'telefon': member_data.getProperty('telefon'),
                'ubicacio': member_data.getProperty('ubicacio'),
                }

