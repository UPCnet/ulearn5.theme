
from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _


class IMyCommunitiesPortlet(IPortletDataProvider):
    """ A portlet which can render the communities subscribed.
    """


class Assignment(base.Assignment):
    implements(IMyCommunitiesPortlet)

    title = _(u'mycommunities', default=u'My Communities')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('mycommunities.pt')

    def update(self):
        self.favorites = self.get_favorites()

    def get_my_communities(self):
        pc = getToolByName(self.context, "portal_catalog")
        results = pc.searchResults(portal_type="ulearn.community")
        return results

    def is_community_manager(self, community):
        pm = getToolByName(self.context, "portal_membership")
        current_user = pm.getAuthenticatedMember().getUserName()
        return current_user == community.Creator

    def get_favorites(self):
        pm = getToolByName(self.context, "portal_membership")
        pc = getToolByName(self.context, "portal_catalog")
        current_user = pm.getAuthenticatedMember().getUserName()

        results = pc.unrestrictedSearchResults(favoritedBy=current_user)
        return [favorites.id for favorites in results]

    def get_star_class(self, community):
        return community.id in self.favorites and 'fa-icon-star' or 'fa-icon-star-empty'


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
