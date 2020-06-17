# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from repoze.catalog.query import Eq
from souper.soup import get_soup
from zope.interface import implements

from ulearn5.core import _
from ulearn5.core.content.community import ICommunity
from ulearn5.theme.portlets.communities import Renderer as RendererCommunities


class IMyCommunitiesNavigation(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(IMyCommunitiesNavigation)

    title = _(u'mycommunities', default=u'My Communities portlet')


class Renderer(RendererCommunities):

    render = ViewPageTemplateFile('mycommunities.pt')

    def getTypeCommunities(self, typeCommunity):
        portal = self.portal()
        pc = getToolByName(portal, "portal_catalog")
        communities = pc.searchResults(object_provides=ICommunity.__identifier__,
                                       community_type=typeCommunity,
                                       sort_on="sortable_title")

        result = self.format_communities_and_check_subscrition(communities)
        return result if len(result) > 0 else None

    def format_communities_and_check_subscrition(self, communities):
        """ Generator to return information of the community.
        """
        result = []
        username = api.user.get_current().id.lower()
        if username != "admin":
            portal = api.portal.get()
            soup = get_soup('communities_acl', portal)

            check = False
            for community in communities:
                records = [r for r in soup.query(Eq('gwuuid', community.gwuuid))]
                if records:
                    if username in [a['id'] for a in records[0].attrs['acl']['users']]:
                        check = True

                    if not check:
                        user_groups = [group.id for group in api.group.get_groups(username=username)]
                        if user_groups:
                            for groups in user_groups:
                                if 'groups' in records[0].attrs['acl']:
                                    if user_groups in [a['id'] for a in records[0].attrs['acl']['groups']]:
                                        check = True

                    if check:
                        if community.tab_view == 'Documents':
                            url = community.getURL() + '/documents'
                        else:
                            url = community.getURL()
                        info = {'id': community.id,
                                'url': url,
                                'title': community.Title,
                                'community_type': community.community_type,
                                'image': obj.image,
                                'pending': self.get_pending_community_user(community, username)
                                }
                        result.append(info)

        return result


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
