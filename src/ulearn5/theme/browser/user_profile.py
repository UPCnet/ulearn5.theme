from OFS.Image import Image

from zope.interface import implements
from zope.component import getUtility
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.component import getUtilitiesFor

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from souper.interfaces import ICatalogFactory

from base5.core.utils import get_safe_member_by_id
from ulearn5.core import _

from plone import api
from mrs5.max.utilities import IMAXClient
import urllib
from Products.CMFCore.utils import getToolByName
from ulearn5.core.adapters.portrait import convertSquareImage


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
            maxclient, settings = getUtility(IMAXClient)()
            foto = maxclient.people[id].avatar
            imageUrl = foto.uri + '/large'

            portrait = urllib.urlretrieve(imageUrl)

            scaled, mimetype = convertSquareImage(portrait[0])
            portrait = Image(id=id, file=scaled, title=id)

            membertool = getToolByName(self, 'portal_memberdata')
            membertool._setPortrait(portrait, id)
            import transaction
            transaction.commit()

            member_info = get_safe_member_by_id(self.user_info.id)
            if member_info.get('fullname', False) \
               and member_info.get('fullname', False) != self.username \
               and member_info.get('email', False) \
               and isinstance(portrait, Image) and portrait.size != '3566':
                return True
                # 3566 is the size of defaultUser.png I don't know how get image
                # title. This behavior is reproduced in profile portlet.
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
