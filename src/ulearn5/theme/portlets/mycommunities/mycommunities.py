# -*- coding: utf-8 -*-
from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ulearn5.core import _
from ulearn5.core.content.community import ICommunity
from ulearn5.core.utils import get_or_initialize_annotation
from ulearn5.theme.portlets.communities import Renderer as RendererCommunities
from zope.interface import implementer


class IMyCommunitiesNavigation(IPortletDataProvider):
    """A portlet which can render the logged user profile information."""


@implementer(IMyCommunitiesNavigation)
class Assignment(base.Assignment):

    title = _("mycommunities", default="My Communities portlet")


class Renderer(RendererCommunities):

    render = ViewPageTemplateFile("mycommunities.pt")

    def getTypeCommunities(self, typeCommunity):
        pc = api.portal.get_tool(name="portal_catalog")
        communities = pc.searchResults(
            object_provides=ICommunity.__identifier__,
            community_type=typeCommunity,
            sort_on="sortable_title",
        )

        result = self.format_communities_and_check_subscrition(communities)
        return result if len(result) > 0 else None

    def format_communities_and_check_subscrition(self, communities):
        """Generator to return information of the community."""
        result = []
        username = api.user.get_current().id.lower()
        if username != "admin":
            portal = api.portal.get()
            communities_acl = get_or_initialize_annotation("communities_acl")

            for community in communities:
                # Reiniciamos la variable de control para cada comunidad.
                check = False
                # Buscamos el registro correspondiente al community.gwuuid
                record = next((r for r in communities_acl.values() if r.get('gwuuid') == community.gwuuid), None)
                if record:
                    # Comprobamos si el usuario aparece en los usuarios del ACL
                    acl_users = record.get('acl', {}).get('users', [])
                    if username in [a.get("id") for a in acl_users]:
                        check = True

                    # Si aún no está, comprobamos si el usuario pertenece a alguno de los grupos listados
                    if not check:
                        user_groups = [group.id for group in api.group.get_groups(username=username)]
                        if user_groups:
                            acl_groups = record.get('acl', {}).get('groups', [])
                            # Se comprueba cada grupo del usuario
                            for group in user_groups:
                                if group in [a.get("id") for a in acl_groups]:
                                    check = True
                                    break

                    if check:
                        if community.tab_view == "Documents":
                            url = community.getURL() + "/documents"
                        else:
                            url = community.getURL()
                        info = {
                            "id": community.id,
                            "url": url,
                            "title": community.Title,
                            "community_type": community.community_type,
                            "image": community.getObject().image,
                            "pending": self.get_pending_community_user(community, username),
                        }
                        result.append(info)
        return result


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
