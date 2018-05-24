# -*- coding: utf-8 -*-
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from zope import schema

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.component.hooks import getSite
from plone.memoize.view import memoize_contextless
from DateTime.DateTime import DateTime


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
        catalog = getToolByName(context, 'portal_catalog')
        now = DateTime()
        results = catalog(portal_type='News Item',
                          review_state=state,
                          path=path,
                          expires={'query': now, 'range': 'min', },
                          effective={'query': now, 'range': 'max', },
                          sort_on='effective',
                          is_important=True,
                          sort_order='reverse',
                          sort_limit=limit)
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
                text = self.abrevia(noticiaObj.text.raw, 100)

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
                    'title': self.abrevia(noticia.Title, 70),
                    'new': noticiaObj,
                    'date': str(news_day) + '/' + str(news_month) + '/' + str(news_year),
                    'image': noticiaObj.image
                    }

            dades.append(info)
        return dades

    def abrevia(self, summary, sumlenght):
        """ Retalla contingut de cadenes
        """
        bb = ''

        if sumlenght < len(summary):
            bb = summary[:sumlenght]

            lastspace = bb.rfind(' ')
            cutter = lastspace
            precut = bb[0:cutter]

            if precut.count('<b>') > precut.count('</b>'):
                cutter = summary.find('</b>', lastspace) + 4
            elif precut.count('<strong>') > precut.count('</strong>'):
                cutter = summary.find('</strong>', lastspace) + 9
            bb = summary[0:cutter]

            if bb.count('<p') > precut.count('</p'):
                bb += '...</p>'
            else:
                bb = bb + '...'
        else:
            bb = summary

        return bb


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
