# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from zope.publisher.browser import BrowserView
from plone import api


class getNews(BrowserView):
    """ Return public news for login page"""

    def __call__(self, *args, **kwargs):
        pc = api.portal.get_tool('portal_catalog')
        now = DateTime()
        results = pc.unrestrictedSearchResults(portal_type='News Item',
                                               review_state='published',
                                               expires={'query': now, 'range': 'min', },
                                               effective={'query': now, 'range': 'max', },
                                               sort_on='effective',
                                               sort_order='reverse',
                                               sort_limit=3
                                               )
        noticies = []
        for noticia in results:
            noticiaObj = noticia._unrestrictedGetObject()
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
                    'date': str(news_day) + '/' + str(news_month) + '/' + str(news_year),
                    'image': noticia.getURL() + '/@@images/image/mini',
                    'subject': noticiaObj.subject,
                    }

            noticies.append(info)

        return noticies

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
