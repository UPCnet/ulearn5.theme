# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFPlone import PloneMessageFactory as _PFM
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from repoze.catalog.query import Eq
from souper.soup import get_soup
from zope import schema
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implements

from base5.core.utils import abrevia
from ulearn5.core import _
from ulearn5.core.utils import getSearchersFromUser

import transaction


class IButtonBarPortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """
    count = schema.Int(title=_PFM(u'Number of items to display'),
                       description=_PFM(u'How many items to list.'),
                       required=True,
                       default=10)

    state = schema.Tuple(title=_PFM(u"Workflow state"),
                         description=_PFM(u"Items in which workflow state to show."),
                         default=('published', 'intranet'),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.WorkflowStates")
                         )


class Assignment(base.Assignment):
    implements(IButtonBarPortlet)

    def __init__(self, count=10, state=('published', 'intranet')):
        self.count = count
        self.state = state

    title = _(u'buttonbar', default=u'Button bar')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('buttonbar.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def is_activate_sharedwithme(self):
        if (api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.elasticsearch') != 'localhost') and (api.portal.get_registry_record('ulearn5.core.controlpanel.IUlearnControlPanelSettings.activate_sharedwithme') == True):
            portal = api.portal.get()
            if portal.portal_actions.object.local_roles.visible is False:
                portal.portal_actions.object.local_roles.visible = True
                transaction.commit()
            return True
        else:
            return False

    def is_activate_news(self):
        return api.portal.get_registry_record('ulearn5.core.controlpanel.IUlearnControlPanelSettings.activate_news')

    def getClass(self):
        """ Returns class for links """
        shared = self.is_activate_sharedwithme()
        news = self.is_activate_news()
        width = ''
        if shared and news:
            width = 'col-md-3 col-sm-3 col-xs-3'
        elif shared and not news:
            width = 'col-md-4 col-sm-4 col-xs-4'
        elif news and not shared:
            width = 'col-md-4 col-sm-4 col-xs-4'
        else:
            width = 'col-md-6 col-sm-6 col-xs-6'

        return "bubble top " + width

    # Subscribed news

    def news_to_show(self):
        return self.data.count > 0 and len(self._data())

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

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
        return getSearchersFromUser()

    def get_news(self, context, state, path, limit):
        catalog = api.portal.get_tool(name='portal_catalog')
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
                    text = abrevia(noticiaObj.description, 150)
                else:
                    text = abrevia(noticiaObj.text.raw, 150)

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
                    'image': noticiaObj.image,
                    'subject': noticiaObj.subject,
                    }

            dades.append(info)

        return dades


class AddForm(base.AddForm):
    schema = IButtonBarPortlet
    label = _(u"Add Subscribed News Portlet")
    description = _(u"This portlet displays subscribed News Items.")

    def create(self, data):
        return Assignment(count=data.get('count', 10),
                          state=data.get('state', ('intranet', )))


class EditForm(base.EditForm):
    schema = IButtonBarPortlet
    label = _(u"Edit Subscribed News Portlet")
    description = _(u"This portlet displays subscribed News Items.")
