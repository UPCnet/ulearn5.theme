# -*- coding: utf-8 -*-
from five.grok import adapter
from five.grok import implementer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from base5.core.portlets.smart.renderers.interfaces import IPortletItemRenderer
from base5.core.portlets.smart.renderers.renderers import PortletItemRenderer

from ulearn5.core.content.video_embed import IVideoEmbed
from ulearn5.core.interfaces import IVideo

import re


YOUTUBE_REGEX = re.compile(r'youtube.*?(?:v=|embed\/)([\w\d-]+)', re.IGNORECASE)
MEDIA_REGEX = re.compile(r'.aac|.f4v|.flac|.m4v|.mkv|.mov|.mp3|.mp4|.oga|.ogg|.ogv|.webm', re.IGNORECASE)

@adapter(IVideoEmbed)
@implementer(IPortletItemRenderer)
class YTVideoPortletItemRenderer(PortletItemRenderer):
    title = "Youtube view"
    css_class = 'carousel-video-yt'

    @property
    def template(self):
        embed_type, code = self.getEmbed()
        try:
            template = ViewPageTemplateFile('templates/{}.pt'.format(embed_type))
        except ValueError:
            template = ViewPageTemplateFile('templates/default.pt')
        return template

    def getVideo(self):
        embed_type, code = self.getEmbed()
        return code

    def getEmbed(self):
        is_youtube_video = YOUTUBE_REGEX.search(self.item.video_url)
        if is_youtube_video:
            return ('youtube', is_youtube_video.groups()[0])

    def getTitle(self):
        item = self.item.getObject()
        return self.abrevia(item.title, 80)

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


@adapter(IVideo)
@implementer(IPortletItemRenderer)
class VideoPortletItemRenderer(PortletItemRenderer):
    title = "Video view"
    css_class = 'carousel-video'

    @property
    def template(self):
        embed_type, code = self.getEmbed()
        try:
            template = ViewPageTemplateFile('templates/{}.pt'.format(embed_type))
        except ValueError:
            template = ViewPageTemplateFile('templates/video_default.pt')
        return template

    def getEmbed(self):
        is_media = MEDIA_REGEX.search(self.getFilename())
        if is_media:
            return ('video', is_media.group())

        return (None, None)

    def getFilename(self):
        return self.item.file.filename

    def getType(self):
        is_media = MEDIA_REGEX.search(self.getFilename())
        return is_media.group()[1::]

    def getTitle(self):
        item = self.item.getObject()
        return self.abrevia(item.title, 80)

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
