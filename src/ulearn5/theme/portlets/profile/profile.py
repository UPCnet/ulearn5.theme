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

from zope.component import getUtility
from mrs5.max.utilities import IMAXClient
from ulearn5.core.adapters.portrait import convertSquareImage
import urllib
from Products.CMFCore.utils import getToolByName


class IProfilePortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information. """


class Assignment(base.Assignment):
    implements(IProfilePortlet)

    title = _(u'profile', default=u'User profile')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('profile.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.username = api.user.get_current().id
        self.user_info = get_safe_member_by_id(self.username)
        self.portal_url = api.portal.get().absolute_url()

    def is_admin_user(self):
        if api.user.get_current().id == 'admin':
            return True
        else:
            return False

    def fullname(self):
        if self.user_info:
            fullname = self.user_info.get('fullname', '')
        else:
            fullname = None

        if fullname:
            return fullname
        else:
            return self.username

    def get_portrait(self):
        pm = api.portal.get_tool('portal_membership')
        return pm.getPersonalPortrait().absolute_url()

    def has_complete_profile(self):
        if self.user_info:
            id = self.user_info['id']
            maxclient, settings = getUtility(IMAXClient)()
            foto = maxclient.people[id].avatar
            imageUrl = foto.uri + '/large'

            portrait = urllib.urlretrieve(imageUrl)

            scaled, mimetype = convertSquareImage(portrait[0])
            portrait = Image(id=id, file=scaled, title=id)

            membertool = getToolByName(self, 'portal_memberdata')
            membertool._setPortrait(portrait, str(id))
            import transaction
            transaction.commit()

            member_info = get_safe_member_by_id(id)
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

    def has_webmaster_role(self):
        return 'WebMaster' in api.user.get_roles()

    def get_badges(self):
        """ Done consistent with an hipotetical badge provider backend """
        # Call to the REST service for the user badges returning a list with the
        # (for example 4 more recent badges or the user selected badges)
        # >>> connect_backpack(self.username.getId(), app="ulearn", sort="user_preference", limit=4)
        # >>> [{"displayName": "Code Whisperer", "id":"codewhisperer", "png": "http://...", "icon": "trophy"}, ]

        badges = deepcopy(AVAILABLE_BADGES)
        if self.has_complete_profile():
            badges[0]['awarded'] = True

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)

        thinnkins = self.get_thinnkins()
        if thinnkins:
            if (thinnkins >= int(settings.threshold_winwin1)):
                badges[1]['awarded'] = True
            if (thinnkins >= int(settings.threshold_winwin2)):
                badges[2]['awarded'] = True
            if (thinnkins >= int(settings.threshold_winwin3)):
                badges[3]['awarded'] = True

        return badges

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

    def userCheckDisplay(self):
        user = api.user.get_current()
        return user.getProperty('visible_userprofile_portlet', True)

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

    def get_url(self, community):
        return self.portal_url + '/' + community.getPhysicalPath()[-1]

    def isCurrentPage(self, page):
        param = False
        path = self.context.absolute_url_path()
        if page in path:
            param = True
        return param

    def get_community_type(self, community):
        return community.community_type

    def get_edit_literal(self):
        """ Get string literal for edit """
        lang = pref_lang()
        if 'ca' in lang:
            return "Editar la comunitat"
        elif 'es' in lang:
            return "Editar la comunidad"
        else:
            return "Edit community"

    def get_acl_literal(self):
        """ Get string literal for editacl """
        lang = pref_lang()
        if 'ca' in lang:
            return "Gestiona els membres"
        elif 'es' in lang:
            return "Gestiona los miembros"
        else:
            return "Manage members"

    def get_com_type_literal(self):
        """ Get string literal for community type """
        lang = pref_lang()
        if 'ca' in lang:
            return "Canvia el tipus de comunitat"
        elif 'es' in lang:
            return "Cambia el tipo de comunidad"
        else:
            return "Change community type"


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
