# -*- coding: utf-8 -*-
from OFS.Image import Image
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.registry.interfaces import IRegistry
from souper.interfaces import ICatalogFactory
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound

from base5.core import _
from base5.core.utils import get_safe_member_by_id
from ulearn5.core.controlpanel import IUlearnControlPanelSettings
from souper.soup import get_soup
from repoze.catalog.query import Eq


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
            self.fullname = self.user_fullname
        else:
            raise NotFound(self, name, request)
        return self

    def get_posts_literal(self):
        literal = api.portal.get_registry_record(name='ulearn5.core.controlpanel.IUlearnControlPanelSettings.people_literal')
        if literal == 'thinnkers':
            return 'thinnkins'
        else:
            return 'entrades'

    def has_complete_profile(self):
        if self.user_info:
            id = self.user_info.id
            portal = api.portal.get()
            soup_users_portrait = get_soup('users_portrait', portal)
            exist = [r for r in soup_users_portrait.query(Eq('id_username', id))]
            if exist:
                user_record = exist[0]
                return user_record.attrs['portrait']
            else:
                return False
        else:
            # The user doesn't have any property information for some weird
            # reason or simply beccause we are admin
            return False

    def get_badges_info(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)

        info = {
            'profile': {
                'title': _(u'Complete the profile'),
                'num': 0,
            },
            'winwin1': {
                'title': self.context.translate(_(u'badge_title', default=u'Contribute ${num} posts', mapping={u'num': settings.threshold_winwin1})),
                'num': settings.threshold_winwin1,
            },
            'winwin2': {
                'title': self.context.translate(_(u'badge_title', default=u'Contribute ${num} posts', mapping={u'num': settings.threshold_winwin2})),
                'num': settings.threshold_winwin2,
            },
            'winwin3': {
                'title': self.context.translate(_(u'badge_title', default=u'Contribute ${num} posts', mapping={u'num': settings.threshold_winwin3})),
                'num': settings.threshold_winwin3,
            }
        }

        return info

    def get_user_info_for_display(self):
        user_properties_utility = getUtility(ICatalogFactory, name='user_properties')

        extender_name = api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender')

        portal = api.portal.get()
        current_user = api.user.get_current().id
        roles = api.user.get_roles(username=current_user, obj=portal)
        can_view_properties = True if current_user == self.username or 'WebMaster' in roles or 'Manager' in roles else False

        rendered_properties = []
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            for prop in extended_user_properties_utility.profile_properties:
                check = self.user_info.getProperty('check_' + prop, '')
                if can_view_properties or check == '' or check:
                    rendered_properties.append(dict(
                        name=_(prop),
                        value=self.user_info.getProperty(prop, '')
                    ))
            return rendered_properties
        else:
            # If it's not extended, then return the simple set of data we know
            # about the user using also the profile_properties field
            for prop in user_properties_utility.profile_properties:
                check = self.user_info.getProperty('check_' + prop, '')
                if can_view_properties or check == '' or check:
                    rendered_properties.append(dict(
                        name=_(prop),
                        value=self.user_info.getProperty(prop, '')
                    ))
            return rendered_properties

    def get_public_user_info_for_display(self):
        extender_name = api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender')

        rendered_properties = []

        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            for prop in extended_user_properties_utility.public_properties:
                rendered_properties.append(dict(
                    name=_(prop),
                    value=self.user_info.getProperty(prop, '')
                ))
        return rendered_properties

    def get_private_user_info_for_display(self):
        extender_name = api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender')

        portal = api.portal.get()
        current_user = api.user.get_current().id
        roles = api.user.get_roles(username=current_user, obj=portal)
        can_view_properties = True if current_user == self.username or 'WebMaster' in roles or 'Manager' in roles else False

        rendered_properties = []

        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            for prop in extended_user_properties_utility.profile_properties:
                if can_view_properties and prop not in extended_user_properties_utility.public_properties:
                    rendered_properties.append(dict(
                        name=_(prop),
                        value=self.user_info.getProperty(prop, '')
                    ))
        return rendered_properties

    def separate_public_private_info(self):
        extender_name = api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender')
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            return hasattr(extended_user_properties_utility, 'public_properties')
        return False

    def get_member_data(self):
        return api.user.get_current()

    def user_properties(self):
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

    def is_admin_user(self):
        if api.user.get_current().id == 'admin':
            return True
        return False
