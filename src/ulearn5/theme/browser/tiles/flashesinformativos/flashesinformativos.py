# -*- coding: utf-8 -*-
from zope.component.hooks import getSite
from plone.memoize.view import memoize_contextless

from Products.CMFCore.utils import getToolByName

from ulearn5.core import _
from zope import schema
from DateTime.DateTime import DateTime
import bleach
import bs4
import re

from plone.supermodel.model import Schema
from plone.tiles.tile import Tile


class IFlashesInformativos(Schema):
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


class FlashesInformativos(Tile):

    def __call__(self):
        return self.index()

    @property
    def name(self):
        """return view_type of portlet"""
        return self.data.get('name', '')

    @property
    def count(self):
        """return number of news to show"""
        return self.data.get('count', '')


    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

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

    def abreviaRichText(self, obj, limit):
        """ Retalla contingut segons un limit de caracters sense tags, tanca tags...
        """
        # body = obj.output
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
        limit = self.data['count']
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
                    'title': self.abrevia(a.Title, 90)
                    }

            dades.append(info)

        return dades

        # data = [dict(id=a.id,
        #              url=a.getURL(),
        #              flash=a.getObject(),
        #              image=a.getObject().image,
        #              text=self.abrevia(a.getObject().text.raw, 90),) for a in flashes]
        # return data

    def get_flashesinformatius_folder_url(self):
        url = self.portal().absolute_url() + '/news'
        return url


    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('tile_title', '')