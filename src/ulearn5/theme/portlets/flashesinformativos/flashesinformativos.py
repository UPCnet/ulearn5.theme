# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements

from base5.core.utils import abrevia
from ulearn5.core import _

import bleach
import bs4
import re


class IFlashesInformativosPortlet(IPortletDataProvider):
    """ A portlet which can render Flashes Informativos information.
    """

    name = schema.TextLine(title=_(u"label_navigation_title", default=u"Title"),
                           description=_(u"help_navigation_title",
                                         default=u"The title of the navigation tree."),
                           default=u"",
                           required=False)

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=False,
                       default=4)


class Assignment(base.Assignment):
    implements(IFlashesInformativosPortlet)

    def __init__(self, name="", count=4):
        self.name = name
        self.count = count

    title = _(u'flashes_informativos', default=u'Flashes Informativos')


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('flashesinformativos.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())

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

    def abreviaRichText(self, obj, limit):
        """ Retalla contingut segons un limit de caracters sense tags, tanca tags...
        """
        text_clean_bleach = bleach.clean(obj, tags=['p', 'strong', 'em', 'a', 'b', 'br'], strip=True)

        def fix_tags(html):
            return str(bs4.BeautifulSoup(html))

        def clear_tags(html):
            return re.sub(r'</?.*?>', '', html)

        def retallar(text, limit):
            retallat = text[:limit]
            remaining_word = re.search(r'^([^\s]*).*?(?:\s|$)', text[limit:]).groups()[0]
            return retallat + remaining_word

        text_with_tags_fixed = fix_tags(text_clean_bleach)
        text_sense_format = clear_tags(text_with_tags_fixed)

        if len(text_sense_format) <= limit:
            return text_with_tags_fixed

        limit2 = int(limit)
        text_sense_format = ''
        while len(text_sense_format) <= limit:
            desc_text = text_clean_bleach[:limit2]
            desc_text = retallar(text_clean_bleach, limit2)
            text_with_tags_fixed = fix_tags(desc_text + '...')
            text_sense_format = clear_tags(text_with_tags_fixed)

            limit2 += 30

            if len(text_clean_bleach) == len(desc_text):
                break

        return text_with_tags_fixed

    def getFlashesInformativos(self):
        portal = self.portal()
        pc = getToolByName(portal, "portal_catalog")
        limit = self.data.count
        now = DateTime()

        # start = DateTime('1969/12/31 00:00:00 GMT+2')  # Fecha effectiva por defecto
        # date_range_query = {'query': (start, now), 'range': 'min:max'}

        flashes = pc.searchResults(portal_type=['News Item'],
                                   expires={'query': now, 'range': 'min', },
                                   effective={'query': now, 'range': 'max', },
                                   sort_on='effective',
                                   sort_order='reverse',
                                   sort_limit=limit,
                                   is_flash=True)[:limit]
        dades = []
        for a in flashes:
            if a.getObject().text is None:
                text = None
            else:
                text = self.abreviaRichText(a.getObject().text.raw, 90)

            info = {'id': a.id,
                    'url': a.getURL(),
                    'flash': a.getObject(),
                    'image': a.getObject().image,
                    'text': text,
                    'title': abrevia(a.Title, 90)
                    }

            dades.append(info)

        return dades

    def get_flashesinformatius_folder_url(self):
        url = self.portal().absolute_url() + '/news'
        return url


class AddForm(base.AddForm):
    schema = IFlashesInformativosPortlet
    label = _(u"Add Flashes Informativos Portlet")
    description = _(u"This portlet displays Flashes Informativos.")

    def create(self, data):
        return Assignment(name=data.get('name', ""), count=data.get('count', 5))


class EditForm(base.EditForm):
    schema = IFlashesInformativosPortlet
    label = _(u"Edit Flashes Informativos portlet")
    description = _(u"This portlet displays Flashes Informativos.")
