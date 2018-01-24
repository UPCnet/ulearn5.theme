# -*- coding: utf-8 -*-
from five import grok
from Acquisition import aq_inner, aq_chain
from cgi import escape
from plone import api
from zope.interface import Interface
from zope.component import getMultiAdapter, getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.layout.viewlets.common import TitleViewlet
from plone.app.layout.viewlets.interfaces import IHtmlHead, IPortalHeader, IAboveContent, IPortalFooter
from ulearn5.theme.interfaces import IUlearn5ThemeLayer
from ulearn5.core.browser.viewlets import viewletBase
from ulearn5.core.controlpanel import IUlearnControlPanelSettings
from plone.registry.interfaces import IRegistry
from souper.soup import get_soup
from souper.soup import Record
from repoze.catalog.query import Eq
from plone.memoize import forever
from ulearn5.core.content.community import ICommunity
from ulearn5.core.interfaces import IDocumentFolder, ILinksFolder, IPhotosFolder, IEventsFolder, IDiscussionFolder

import datetime

grok.context(Interface)


class viewletBaseUlearn(viewletBase):
    grok.baseclass()


class TitleViewlet(TitleViewlet, viewletBase):
    grok.context(Interface)
    grok.name('plone.htmlhead.title')
    grok.viewletmanager(IHtmlHead)
    grok.layer(IUlearn5ThemeLayer)

    def update(self):
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        page_title = escape(safe_unicode(context_state.object_title()))
        marcaUlearn = escape(safe_unicode(u"Ulearn Comunidades"))
        self.site_title = u"%s - %s" % (page_title, marcaUlearn)


class viewletHeaderUlearn(viewletBase):
    grok.name('ulearn.header')
    grok.template('header')
    grok.viewletmanager(IPortalHeader)
    grok.layer(IUlearn5ThemeLayer)

    def is_info_servei_activate(self):
        servei = api.portal.get_registry_record('ulearn5.core.controlpanel.IUlearnControlPanelSettings.info_servei')
        if not servei:
            return False
        else:
            return True

    def info_servei(self):
        return api.portal.get_registry_record('ulearn5.core.controlpanel.IUlearnControlPanelSettings.info_servei')

    def quickLinks(self):
        """ Return quicklinks for language """
        lang = self.pref_lang()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)

        text = None
        if settings.quicklinks_literal is not None:
            for item in settings.quicklinks_literal:
                if lang in item['language']:
                    text = item['text']
                    break

        items = []
        if settings.quicklinks_table is not None:
            for item in settings.quicklinks_table:
                if lang in item['language']:
                    items.append(item)

        if len(items) > 0:
            quicklinks_show = True
        else:
            quicklinks_show = False

        dades = {'quickLinksLiteral': text,
                 'quickLinksIcon': settings.quicklinks_icon,
                 'quickLinksTable': items,
                 'quickLinksShow': quicklinks_show,
                 }

        return dades

    def canManage(self):
        current = api.user.get_current()
        portal = api.portal.get()
        if 'gestion' in portal:
            roles = api.user.get_roles(username=current.id, obj=portal['gestion'])
            if 'Reader' in roles or 'Editor' in roles or 'Contributor' in roles or 'Reviewer' in roles or 'WebMaster' in roles or 'Manager' in roles:
                return True
            else:
                return False
        else:
            return False

    def canManageMenu(self):
        current = api.user.get_current()
        portal = api.portal.get()
        if 'gestion' in portal and 'menu' in portal['gestion']:
            roles = api.user.get_roles(username=current.id, obj=portal['gestion']['menu'])
            if 'Reader' in roles or 'Editor' in roles or 'Contributor' in roles or 'WebMaster' in roles or 'Manager' in roles:
                return True
            else:
                return False
        return False

    def canResetMenu(self):
        current = api.user.get_current()
        portal = api.portal.get()
        if 'gestion' in portal and 'menu' in portal['gestion']:
            roles = api.user.get_roles(username=current.id, obj=portal['gestion']['menu'])
            if 'Editor' in roles or 'Contributor' in roles or 'WebMaster' in roles or 'Manager' in roles:
                return True
            else:
                return False
        return False

    def _createLinksMenu(self, language):
        """ Genera el menu de enlaces segun el idioma que tenga definido el
            usuario en su perfil
        """
        portal = api.portal.get()
        if 'gestion' in portal and 'menu' in portal['gestion'] and language in portal['gestion']['menu']:
            menu = portal['gestion']['menu'][language]
            path_language = "/".join(menu.getPhysicalPath())

            catalog = api.portal.get_tool(name='portal_catalog')
            folders = catalog(portal_type=('Folder', 'privateFolder'),
                              review_state='intranet',
                              path={'query': path_language, 'depth': 1},
                              sort_on="getObjPositionInParent")

            carpetes = {}
            for folder in folders:
                path = folder.getPath()
                carpeta = {'id': folder.id,
                           'title': folder.getObject().title,
                           'url': folder.getURL(),
                           'links': []
                           }
                carpetes[path] = carpeta

            res = catalog(portal_type='Link',
                          review_state='intranet',
                          path={'query': path_language, 'depth': 2},
                          sort_on="getObjPositionInParent")

            links = []
            links.extend(res)
            for link in links:
                obj = link.getObject()
                link_parent_path = "/".join(obj.__parent__.getPhysicalPath())
                info = {'id': obj.id,
                        'title': obj.title,
                        'url': obj.remoteUrl,
                        'new_window': obj.open_link_in_new_window,
                        }
                try:
                    carpetes[link_parent_path]['links'].append(info)
                except:
                    pass

            return carpetes
        else:
            return {}

    def linksMenu(self):
        """ Devuelve el menu de enlaces segun el idioma que tenga definido el
            usuario en su perfil
        """
        current = api.user.get_current()
        user_language = current.getProperty('language')
        if user_language == '':
            lt = getToolByName(self.portal(), 'portal_languages')
            user_language = lt.getPreferredLanguage()
            current.setMemberProperties({'language': user_language})

        portal = api.portal.get()
        soup_menu = get_soup('menu_soup', portal)
        exist = [r for r in soup_menu.query(Eq('id_menusoup', user_language))]
        if not exist:
            dades = self._createLinksMenu(user_language)
            record = Record()
            record.attrs['id_menusoup'] = user_language
            record.attrs['dades'] = dades.values()
            soup_menu.add(record)
            soup_menu.reindex()
            return dades.values()
        else:
            return exist[0].attrs['dades']


class folderBar(viewletBase):
    grok.name('ulearn.folderbar')
    grok.template('folderbar')
    grok.viewletmanager(IAboveContent)
    grok.layer(IUlearn5ThemeLayer)

    def update(self):
        context = aq_inner(self.context)
        self.folder_type = ''
        for obj in aq_chain(context):
            if IDocumentFolder.providedBy(obj):
                self.folder_type = 'documents'
                break
            if ILinksFolder.providedBy(obj):
                self.folder_type = 'links'
                break
            if IPhotosFolder.providedBy(obj):
                self.folder_type = 'photos'
                break
            if IEventsFolder.providedBy(obj):
                self.folder_type = 'events'
                break
            if IDiscussionFolder.providedBy(obj):
                self.folder_type = 'discussion'
                break
            if ICommunity.providedBy(obj):
                self.folder_type = 'community'
                break

    def bubble_class(self, bubble):
        if self.folder_type == 'events' or \
           self.folder_type == 'discussion':
            width = 'col-md-4'
        else:
            width = 'col-md-6'

        if bubble == self.folder_type:
            return 'active bubble top {}'.format(width)
        elif bubble == 'documents' and 'photos' == self.folder_type:
            return 'active bubble top {}'.format(width)
        else:
            return 'bubble top {}'.format(width)

    def get_community(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return obj

    def render_viewlet(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True
        return False

class viewletFooterUlearn(viewletBase):
    grok.name('ulearn.footer')
    grok.template('footer')
    grok.viewletmanager(IPortalFooter)
    grok.layer(IUlearn5ThemeLayer)

    @forever.memoize
    def get_current_year(self):
        return datetime.datetime.now().year
