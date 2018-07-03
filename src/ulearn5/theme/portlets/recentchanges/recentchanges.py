# from plone.memoize import ram
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets import PloneMessageFactory as _PMF
from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import implements

from ulearn5.core import _
from ulearn5.core.content.community import ICommunity

import logging

logger = logging.getLogger("Plone")


class IRecentChangesPortlet(IPortletDataProvider):

    name = schema.TextLine(title=_PMF(u"Title"),
                           required=True)

    count = schema.Int(title=_PMF(u'Number of items to display'),
                       required=True,
                       default=6)


class Assignment(base.Assignment):
    implements(IRecentChangesPortlet)

    def __init__(self, name="", count=5):
        self.name = name
        self.count = count

    @property
    def title(self):
        """ Display the name in portlet mngmt interface """
        if self.name:
            return self.name
        return _(u'Recent changes')


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('recentchanges.pt')

    def title(self):
        return self.data.title

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name='plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.navigation_root_url = portal_state.navigation_root_url()
        self.typesToShow = ['Document', 'File', 'Folder', 'Image', 'Link', 'ulearn.video', 'ulearn.video_embed']
        self.navigation_root_path = portal_state.navigation_root_path()

        plone_tools = getMultiAdapter((context, self.request), name='plone_tools')
        self.catalog = plone_tools.catalog()

    def render(self):
        return xhtml_compress(self._template())

    def recent_items(self):
        return self._data()

    def _data(self):
        limit = self.data.count
        query = {'sort_on': 'modified',
                 'path': {'query': self.getRootPath()},
                 'portal_type': self.typesToShow,
                 'sort_order': 'reverse',
                 'sort_limit': limit}

        items = self.catalog(**query)[:limit]
        results = []
        if items:
            for item in items:
                value = item.getObject()
                if item.Description:
                    if len(item.Description) > 110:
                        itemdescr = item.Description[:110] + '...'
                    else:
                        itemdescr = item.Description
                else:
                    itemdescr = ''

                community_type = value.community_type if hasattr(value, 'community_type') else "notCommunity"

                results += [{'item_title': item.Title,
                             'item_description': itemdescr,
                             'portal_type': value.portal_type.replace('.', '-'),
                             'getURL': item.getURL(),
                             'review_state': item.review_state,
                             'creator': item.Creator,
                             'community_type': community_type,
                             'ModificationDate': value.modification_date.strftime('%d/%m')
                             }]
            return results
        else:
            return None

    def isCommunity(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True

        return False

    def getRootPath(self):
        portal = api.portal.get()
        if self.isCommunity():
            community = aq_inner(self.context)
            for obj in aq_chain(community):
                if ICommunity.providedBy(obj):
                    community_path = obj.getPhysicalPath()
                    break
            return '/'.join(community_path)
        else:
            portal_path = portal.getPhysicalPath()
            return '/'.join(portal_path)


class AddForm(base.AddForm):
    schema = IRecentChangesPortlet
    label = _(u"Add Recent Changes Portlet")
    description = _(u"This portlet displays recently modified content.")

    def create(self, data):
        return Assignment(name=data.get('name', ""), count=data.get('count', 5))


class EditForm(base.EditForm):
    schema = IRecentChangesPortlet
    label = _(u"Edit Recent Changes Portlet")
    description = _(u"This portlet displays recently modified content.")
