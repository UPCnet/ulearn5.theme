# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implements

from base5.core.utils import abrevia
from ulearn5.core import _


class IImportantNewsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=4)

    state = schema.Tuple(title=_(u"Workflow state"),
                         description=_(u"Items in which workflow state to show."),
                         default=('published', 'intranet'),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.WorkflowStates")
                         )


class Assignment(base.Assignment):
    implements(IImportantNewsPortlet)

    def __init__(self, count=6, state=('published', 'intranet')):
        self.count = count
        self.state = state

    title = _(u'importantnews', default=u'Important News')


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('importantnews.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    # @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @memoize_contextless
    def portal(self):
        return getSite()

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def published_news_items(self):
        return self._data()

    def get_noticias_folder_url(self):
        url = self.portal().absolute_url() + '/news'
        return url

    def dadesNoticies(self):
        noticies = self._data()
        return noticies

    def id_noticies(self, noticies):
        info_id = []
        for item in noticies:
            info_id.append(item['id'])

        return info_id

    @memoize
    def _data(self):
        noticies = []
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name='plone_portal_state')
        path = portal_state.navigation_root_path()
        limit = self.data.count
        state = self.data.state

        noticies += self.get_news(context, state, path, limit)

        return noticies

    def get_news(self, context, state, path, limit):
        catalog = api.portal.get_tool(name='portal_catalog')
        now = DateTime()
        results = catalog(portal_type='News Item',
                          review_state=state,
                          is_important=True,
                          expires={'query': now, 'range': 'min', },
                          effective={'query': now, 'range': 'max', },
                          sort_on='effective',
                          sort_order='reverse',
                          sort_limit=limit
                          )[:limit]

        noticies = self.dades(results)
        for item in noticies:
            yield item

    def dades(self, noticies):
        dades = []
        for noticia in noticies:
            noticiaObj = noticia.getObject()
            if noticiaObj.text is None:
                text = None
            else:
                text = abrevia(noticiaObj.text.raw, 100)

            if noticiaObj.effective_date:
                news_day = noticiaObj.effective_date.day()
                news_month = noticiaObj.effective_date.month()
                news_year = noticiaObj.effective_date.year()
            else:
                news_day = noticiaObj.modification_date.day()
                news_month = noticiaObj.modification_date.month()
                news_year = noticiaObj.modification_date.year()

            info = {'id': noticia.id,
                    'text': text,
                    'url': noticia.getURL(),
                    'title': abrevia(noticia.Title, 70),
                    'new': noticiaObj,
                    'date': str(news_day) + '/' + str(news_month) + '/' + str(news_year),
                    'image': noticiaObj.image
                    }

            dades.append(info)
        return dades


class AddForm(base.AddForm):
    schema = IImportantNewsPortlet
    label = _(u"Add News Portlet")
    description = _(u"This portlet displays recent News Items.")

    def create(self, data):
        return Assignment(count=data.get('count', 8),
                          state=data.get('state', ('intranet', )))


class EditForm(base.EditForm):
    schema = IImportantNewsPortlet
    label = _(u"Edit News Portlet")
    description = _(u"This portlet displays recent News Items.")
