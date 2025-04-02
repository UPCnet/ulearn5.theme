# -*- coding: utf-8 -*-
from copy import deepcopy
from hashlib import sha1

from Acquisition import aq_chain, aq_inner
from base5.core.utils import get_safe_member_by_id, pref_lang
from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ulearn5.core import _
from ulearn5.core.badges import AVAILABLE_BADGES
from ulearn5.core.content.community import ICommunity
from ulearn5.core.controlpanel import IUlearnControlPanelSettings
from ulearn5.core.utils import get_or_initialize_annotation
from zope.component import getMultiAdapter, queryUtility
from zope.interface import implementer
from souper.soup import get_soup
from repoze.catalog.query import Eq


class IProfilePortlet(IPortletDataProvider):
    """A portlet which can render the logged user profile information."""


@implementer(IProfilePortlet)
class Assignment(base.Assignment):

    title = _("profile", default="User profile")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile("profile.pt")

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)

        # Solo ejecuta el código si el usuario no es anónimo
        if not api.user.is_anonymous():
            self.username = api.user.get_current().id
            self.user_info = get_safe_member_by_id(self.username)
            self.portal_url = api.portal.get().absolute_url()
        else:
            # Si el usuario es anónimo, inicializa con valores predeterminados
            self.username = None
            self.user_info = None
            self.portal_url = None

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def is_admin_user(self):
        if api.user.get_current().id == "admin":
            return True
        else:
            return False

    def fullname(self):
        if self.user_info:
            fullname = self.user_info.get("fullname", "")
        else:
            fullname = None

        if fullname:
            return fullname
        else:
            return self.username

    def get_portrait(self):
        pm = api.portal.get_tool("portal_membership")
        return pm.getPersonalPortrait().absolute_url()

    def has_complete_profile(self):
        if self.user_info:
            id = self.user_info["id"]
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

    def has_webmaster_role(self):
        return "WebMaster" in api.user.get_roles()

    def get_badges(self):
        """Done consistent with an hipotetical badge provider backend"""
        # Call to the REST service for the user badges returning a list with the
        # (for example 4 more recent badges or the user selected badges)
        # >>> connect_backpack(self.username.getId(), app="ulearn", sort="user_preference", limit=4)
        # >>> [{"displayName": "Code Whisperer", "id":"codewhisperer", "png": "http://...", "icon": "trophy"}, ]

        badges = deepcopy(AVAILABLE_BADGES)
        if self.has_complete_profile():
            badges[0]["awarded"] = True

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)

        thinnkins = self.get_thinnkins()
        if thinnkins:
            if thinnkins >= int(settings.threshold_winwin1):
                badges[1]["awarded"] = True
            if thinnkins >= int(settings.threshold_winwin2):
                badges[2]["awarded"] = True
            if thinnkins >= int(settings.threshold_winwin3):
                badges[3]["awarded"] = True

        return badges

    def get_badges_info(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)

        info = {
            "profile": {
                "title": _("Complete the profile"),
                "num": 0,
            },
            "winwin1": {
                "title": self.context.translate(
                    _(
                        "badge_title",
                        default="Contribute ${num} posts",
                        mapping={"num": settings.threshold_winwin1},
                    )
                ),
                "num": settings.threshold_winwin1,
            },
            "winwin2": {
                "title": self.context.translate(
                    _(
                        "badge_title",
                        default="Contribute ${num} posts",
                        mapping={"num": settings.threshold_winwin2},
                    )
                ),
                "num": settings.threshold_winwin2,
            },
            "winwin3": {
                "title": self.context.translate(
                    _(
                        "badge_title",
                        default="Contribute ${num} posts",
                        mapping={"num": settings.threshold_winwin3},
                    )
                ),
                "num": settings.threshold_winwin3,
            },
        }

        return info

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
        return user.getProperty("visible_userprofile_portlet", True)

    def showEditCommunity(self):
        if (
            not IPloneSiteRoot.providedBy(self.context)
            and ICommunity.providedBy(self.context)
            and "Owner" in api.user.get_roles(username=self.username, obj=self.context)
        ):
            return True

    def get_addable_types(self):
        factories_view = getMultiAdapter(
            (self.context, self.request), name="folder_factories"
        )
        return factories_view.addable_types()

    def get_posts_literal(self):
        literal = api.portal.get_registry_record(
            name="ulearn5.core.controlpanel.IUlearnControlPanelSettings.people_literal"
        )
        if literal == "thinnkers":
            return "thinnkins"
        else:
            return "entrades"

    def get_hash(self, community):
        return sha1(community.absolute_url().encode('utf-8')).hexdigest()

    def get_url(self, community):
        return self.portal_url + "/" + community.getPhysicalPath()[-1]

    def isCurrentPage(self, page):
        param = False
        path = self.context.absolute_url_path()
        if page in path:
            param = True
        return param

    def get_community_type(self, community):
        return community.community_type

    def get_edit_literal(self):
        """Get string literal for edit"""
        lang = pref_lang()
        if "ca" in lang:
            return "Editar la comunitat"
        elif "es" in lang:
            return "Editar la comunidad"
        else:
            return "Edit community"

    def get_acl_literal(self):
        """Get string literal for editacl"""
        lang = pref_lang()
        if "ca" in lang:
            return "Gestiona els membres"
        elif "es" in lang:
            return "Gestiona los miembros"
        else:
            return "Manage members"

    def get_com_type_literal(self):
        """Get string literal for community type"""
        lang = pref_lang()
        if "ca" in lang:
            return "Canvia el tipus de comunitat"
        elif "es" in lang:
            return "Cambia el tipo de comunidad"
        else:
            return "Change community type"

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
