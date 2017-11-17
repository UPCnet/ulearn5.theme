from hashlib import sha1
from plone import api
from Acquisition import aq_inner, aq_chain
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ulearn5.core.content.community import ICommunity

from zope.security import checkPermission
from ulearn5.core import _


class IStatsPortlet(IPortletDataProvider):
    """ A portlet which can render the community stats information """


class Assignment(base.Assignment):
    implements(IStatsPortlet)
    title = _(u'stats', default=u'Stats')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/stats.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.portal_url = api.portal.get().absolute_url()

    def get_hash(self):
        """ Assume that the stats are only shown on the community itself. """
        context = aq_inner(self.context)
        # Light guard
        if ICommunity.providedBy(context):
            return sha1(context.absolute_url()).hexdigest()

    def is_community(self):
        """ Assume that the stats are only shown on the community itself. """
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True

        return False

    def get_stats_for(self, query_type):
        current_path = '/'.join(self.context.getPhysicalPath())

        pc = api.portal.get_tool('portal_catalog')
        if query_type == 'documents':
            results = pc.searchResults(portal_type=['Document', 'File', 'AppFile'], path={'query': current_path})
        elif query_type == 'links':
            results = pc.searchResults(portal_type=['Link'], path={'query': current_path})
        elif query_type == 'media':
            results = pc.searchResults(portal_type=['Image', 'AppImage', 'ulearn.video', 'ulearn.video_embed'], path={'query': current_path})

        return len(results)

    def get_posts_literal(self):
        literal = api.portal.get_registry_record(name='ulearn5.core.controlpanel.IUlearnControlPanelSettings.people_literal')
        if literal == 'thinnkers':
            return 'thinnkins'
        else:
            return _(u'entrades')

    def show_stats(self):
        """ The base.webmaster can see stats.
        """
        if checkPermission('base.webmaster', self.context):
            return True


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
