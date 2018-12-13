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

from plone import api
from souper.soup import get_soup
from repoze.catalog.query import Eq


class ISubscribedNewsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=20)

    state = schema.Tuple(title=_(u"Workflow state"),
                         description=_(u"Items in which workflow state to show."),
                         default=('published', 'intranet'),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.WorkflowStates")
                         )


class Assignment(base.Assignment):
    implements(ISubscribedNewsPortlet)

    def __init__(self, count=20, state=('published', 'intranet')):
        self.count = count
        self.state = state

    @property
    def title(self):
        return _(u"My Subscribed News")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('subscribednews.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    # @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self._data())

    @memoize_contextless
    def portal(self):
        return getSite()

    def published_news_items(self):
        return self._data()

    def get_noticias_folder_url(self):
        url = self.portal().absolute_url() + '/noticies'
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
        news = []
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name='plone_portal_state')
        path = portal_state.navigation_root_path()
        limit = self.data.count
        state = self.data.state

        news += self.get_news(context, state, path, limit)
        if news:
            return news
        else:
            return []

    def getSearchers(self):
        portal = getSite()
        current_user = api.user.get_current()
        userid = current_user.id
        soup_searches = get_soup('user_news_searches', portal)
        exist = [r for r in soup_searches.query(Eq('id', userid))]
        res = []
        if exist:
            values = exist[0].attrs['searches']
            if values:
                for val in values:
                    res.append(' '.join(val))
        return res

    def get_news(self, context, state, path, limit):
        catalog = getToolByName(context, 'portal_catalog')
        now = DateTime()
        results = catalog(portal_type='News Item',
                          review_state=state,
                          path=path,
                          expires={'query': now, 'range': 'min', },
                          effective={'query': now, 'range': 'max', },
                          sort_on='effective',
                          sort_order='reverse',
                          sort_limit=limit,
                          is_outoflist=False
                          )

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
                if noticiaObj.description:
                    text = self.abrevia(noticiaObj.description, 150)
                else:
                    text = self.abrevia(noticiaObj.text.raw, 150)

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
                    'image': noticiaObj.image,
                    'subject': noticiaObj.subject,
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
    schema = ISubscribedNewsPortlet
    label = _(u"Add Subscribed News Portlet")
    description = _(u"This portlet displays subscribed News Items.")

    def create(self, data):
        return Assignment(count=data.get('count', 20), state=data.get('state', ('published', )))


class EditForm(base.EditForm):
    schema = ISubscribedNewsPortlet
    label = _(u"Edit Subscribed News Portlet")
    description = _(u"This portlet displays subscribed News Items.")
