# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from repoze.catalog.query import Eq
from souper.soup import get_soup
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import implements
from zope.security import checkPermission

from ulearn5.core import _
from ulearn5.core.content.community import ICommunity
from ulearn5.core.controlpanel import IUlearnControlPanelSettings


class ICommunitiesNavigation(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(ICommunitiesNavigation)

    title = _(u'communities', default=u'Communities portlet')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/communities.pt')

    @staticmethod
    def get_pending_community_user(community, user):
        """ Returns the number of pending objects to see in the community.
        """
        def get_data_acces_community_user():
            """ Returns the date of user access to the community.
            """
            user_community = user + '_' + community.id
            portal = api.portal.get()

            soup_access = get_soup('user_community_access', portal)
            exist = [r for r in soup_access.query(Eq('user_community', user_community))]
            if not exist:
                return DateTime()
            else:
                return exist[0].attrs['data_access']

        data_access = get_data_acces_community_user() + 0.001   # Suma 0.001 para que no muetre los que acaba de crear el usuario
        now = DateTime() + 0.001  # Suma 0.001 para que no muetre los que acaba de crear el usuario
        pc = api.portal.get_tool(name="portal_catalog")

        date_range_query = {'query': (data_access, now), 'range': 'min:max'}

        results = pc.searchResults(path=community.getPath(),
                                   created=date_range_query)
        valor = len(results)
        if valor > 0:
            return valor
        else:
            return 0

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def get_addview(self):
        add_view = self.portal().restrictedTraverse('{}/addCommunity'.format('/'.join(self.portal().getPhysicalPath())))
        add_view.update()
        return add_view.render()

    def showCreateCommunity(self):
        """ The Contributor role is assumed that will be applied at the group in
            the portal root.
        """
        if 'front-page' in self.context.getPhysicalPath() and \
            checkPermission('ulearn.addCommunity', self.portal()):
            if api.user.get_current().id != "admin":
                return True

    def showEditCommunity(self):
        pm = api.portal.get_tool(name='portal_membership')
        user = pm.getAuthenticatedMember()

        if not IPloneSiteRoot.providedBy(self.context) and \
            ICommunity.providedBy(self.context) and \
            ('Manager' in user.getRoles() or
            'WebMaster' in user.getRoles() or
            'Site Administrator' in user.getRoles() or
            'Owner' in self.context.get_local_roles_for_userid(user.id)):
            return True

    def getTypeCommunities(self, typeCommunity):
        pc = api.portal.get_tool(name="portal_catalog")
        pm = api.portal.get_tool(name="portal_membership")
        current_user = pm.getAuthenticatedMember().getUserName().lower()
        communities = pc.searchResults(object_provides=ICommunity.__identifier__,
                                       favoritedBy=current_user,
                                       community_type=typeCommunity,
                                       sort_on="sortable_title")

        result = self.format_communities(current_user, communities)
        return result if len(result) > 0 else None

    def format_communities(self, current_user, communities):
        """ Generator to return information of the community.
        """
        result = []
        for community in communities:
            obj = community.getObject()
            if obj.tab_view == 'Documents':
                url = community.getURL() + '/documents'
            else:
                url = community.getURL()
            info = {'id': community.id,
                    'url': url,
                    'title': community.Title,
                    'community_type': community.community_type,
                    'image': obj.image,
                    'pending': self.get_pending_community_user(community, current_user)
                    }
            result.append(info)
        return result

    def getOpenCommunities(self):
        """ in GWOPA equals to CoP """
        return self.getTypeCommunities("Open")

    def getOrganizativeCommunities(self):
        """ in GWOPA equals to Corporate """
        return self.getTypeCommunities("Organizative")

    def getClosedCommunities(self):
        """ in GWOPA equals to Wop Team """
        return self.getTypeCommunities("Closed")

    def displayTypeCommunity(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)
        return settings.show_literals

    def getCommunityMembers(self, community):
        if community.subscribed_items < 100:
            return community.subscribed_items
        else:
            return '+99'

    # def get_community_title(self, title):
    #     if len(title) > 18:
    #         return title[:18] + '...'
    #     else:
    #         return title

    def get_campus_url(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)
        return settings.campus_url

    def get_library_url(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)
        return settings.library_url

    def get_user(self):
        pm = api.portal.get_tool(name="portal_membership")
        current_user = pm.getAuthenticatedMember().getUserName()
        return current_user

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
