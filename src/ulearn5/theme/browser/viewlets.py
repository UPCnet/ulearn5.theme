# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode

from cgi import escape
from datetime import datetime as ddatetime
from five import grok
from plone import api
from plone.app.layout.viewlets.common import TitleViewlet
from plone.app.layout.viewlets.interfaces import IAboveContent
from plone.app.layout.viewlets.interfaces import IHtmlHead
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.memoize import forever
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever
from plone.registry.interfaces import IRegistry
from repoze.catalog.query import Eq
from souper.soup import Record
from souper.soup import get_soup
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Interface

from ulearn5.core.browser.viewlets import viewletBase
from ulearn5.core.content.community import ICommunity
from ulearn5.core.controlpanel import IUlearnControlPanelSettings
from ulearn5.core.interfaces import IDocumentFolder
from ulearn5.core.interfaces import IEventsFolder
from ulearn5.core.interfaces import ILinksFolder
from ulearn5.core.interfaces import INewsItemFolder
from ulearn5.core.interfaces import IPhotosFolder

from ulearn5.theme.interfaces import IUlearn5ThemeLayer
from ulearn5.core.hooks import packages_installed

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
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal_title = escape(safe_unicode(portal_state.navigation_root_title()))

        current = api.user.get_current()
        lang = current.getProperty('language')
        titleUlearn = self.context.translate('Ulearn Communities', domain='ulearn', target_language=lang)
        marcaUlearn = escape(safe_unicode(titleUlearn))
        if lang not in ['ca', 'en', 'es']:
            lang = 'ca'
        titleSite = api.portal.get_registry_record('ulearn5.core.controlpanel.IUlearnControlPanelSettings.html_title_' + str(lang))
        if titleSite:
            marcaUlearn = titleSite

        if page_title == portal_title or self.context.id == 'front-page':
            self.site_title = u"%s" % (marcaUlearn)
        else:
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
        if current.getUserName() == 'Anonymous User':
            return False
        portal = api.portal.get()
        if 'gestion' in portal:
            roles = api.user.get_roles(username=current.id, obj=portal['gestion'])
            if 'Editor' in roles or 'Contributor' in roles or 'WebMaster' in roles or 'Manager' in roles or self.canManageMenu() or self.canManageNews() or self.canManageStats() or self.canManageHeader() or self.canManageFooter() or self.canManageBanners() or self.canManagePersonalBanners() or self.viewNominesRootFolder():
                return True
        return False

    def canManageDirectory(self, directory):
        current = api.user.get_current()
        portal = api.portal.get()
        if not api.user.is_anonymous() and 'gestion' in portal and directory in portal['gestion']:
            roles = api.user.get_roles(username=current.id, obj=portal['gestion'][directory])
            if 'Editor' in roles or 'Contributor' in roles or 'Reviewer' in roles or 'WebMaster' in roles or 'Manager' in roles:
                return True
        return False

    def canManageMenu(self):
        return self.canManageDirectory('menu')

    def canManageNews(self):
        current = api.user.get_current()
        portal = api.portal.get()
        if 'news' in portal:
            roles = api.user.get_roles(username=current.id, obj=portal['news'])
            if 'Editor' in roles or 'Contributor' in roles or 'WebMaster' in roles or 'Manager' in roles:
                return True
        return False

    def canManageStats(self):
        current = api.user.get_current()
        portal = api.portal.get()
        roles = api.user.get_roles(username=current.id, obj=portal)
        if 'WebMaster' in roles or 'Manager' in roles:
            return True
        return False

    def canManageHeader(self):
        return self.canManageDirectory('header')

    def canManageFooter(self):
        return self.canManageDirectory('footer')

    def isDisplayedPortletBanners(self, typePortlet):
        columns = ['ContentWellPortlets.BelowTitlePortletManager1',
                   'ContentWellPortlets.BelowTitlePortletManager2',
                   'ContentWellPortlets.BelowTitlePortletManager3',
                   'plone.leftcolumn', 'plone.rightcolumn']
        for column in columns:
            managerColumn = getUtility(IPortletManager, name=column)
            retriever = getMultiAdapter((self.context, managerColumn), IPortletRetriever)
            portlets = retriever.getPortlets()
            for portlet in portlets:
                if 'banners' in portlet['name']:
                    if getattr(portlet['assignment'], 'typePortlet', '') == typePortlet:
                        return True
        return False

    def canManageBanners(self):
        if self.isDisplayedPortletBanners('Global'):
            return self.canManageDirectory('banners')
        return False

    def canManagePersonalBanners(self):
        if self.isDisplayedPortletBanners('Personal'):
            current = api.user.get_current()
            portal = api.portal.get()
            if 'Members' in portal:
                if current.id in portal['Members']:
                    if 'banners' in portal['Members'][current.id]:
                        return True
        return False

    def currentUser(self):
        user = api.user.get_current().id
        return user

    def _createLinksMenu(self, language):
        """ Genera el menu de enlaces segun el idioma que tenga definido el
            usuario en su perfil
        """
        portal = api.portal.get()
        if 'gestion' in portal and 'menu' in portal['gestion'] and language in portal['gestion']['menu']:
            menu = portal['gestion']['menu'][language]
            instance_name = portal.absolute_url()
            path_language = "/".join(menu.getPhysicalPath())

            catalog = api.portal.get_tool(name='portal_catalog')
            folders = catalog(portal_type=('Folder', 'privateFolder'),
                              review_state='intranet',
                              path={'query': path_language, 'depth': 1},
                              sort_on="getObjPositionInParent")

            carpetes = {}
            for pos, folder in enumerate(folders):
                path = folder.getPath()
                carpeta = {'id': folder.id,
                           'position': pos,
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
                url = obj.remoteUrl.replace('${portal_url}', instance_name)
                info = {'id': obj.id,
                        'title': obj.title,
                        'url': url,
                        'new_window': obj.open_link_in_new_window,
                        'icon': obj.awicon
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
        if api.user.is_anonymous():
            pass
        else:
            current = api.user.get_current()
            user_language = current.getProperty('language')
            if not user_language or user_language == '':
                lt = api.portal.get_tool(name='portal_languages')
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
                result = dades.values()
            else:
                result = exist[0].attrs['dades']

            return sorted(result, key=lambda x: x['position'])

    def _createLinksHeader(self, language):
        """ Genera el header segun el idioma que tenga definido el
            usuario en su perfil
        """
        portal = api.portal.get()
        if 'gestion' in portal and 'header' in portal['gestion'] and language in portal['gestion']['header']:
            catalog = api.portal.get_tool(name='portal_catalog')
            portalPath = '/'.join(api.portal.get().getPhysicalPath())
            path = portalPath + '/gestion/header/' + language

            images = catalog.searchResults(portal_type='Image',
                                           path={'query': path, 'depth': 1},
                                           sort_on='getObjPositionInParent')
            if len(images) > 0:
                return images[0].getURL()
            else:
                return None
        else:
            return None

    def get_customized_header(self):
        """ Devuelve el header segun el idioma que tenga definido el
            usuario en su perfil
        """
        if api.user.is_anonymous():
            pass
        else:
            current = api.user.get_current()
            user_language = current.getProperty('language')
            if not user_language or user_language == '':
                lt = api.portal.get_tool(name='portal_languages')
                user_language = lt.getPreferredLanguage()
                current.setMemberProperties({'language': user_language})

            portal = api.portal.get()
            soup_header = get_soup('header_soup', portal)
            exist = [r for r in soup_header.query(Eq('id_headersoup', user_language))]

            if not exist:
                dades = self._createLinksHeader(user_language)
                record = Record()
                record.attrs['id_headersoup'] = user_language
                record.attrs['dades'] = dades
                soup_header.add(record)
                soup_header.reindex()
                result = dades
            else:
                result = exist[0].attrs['dades']

            return result

    def viewNominesRootFolder(self):
        # If package is installed check if its needed to show the button
        installed = packages_installed()
        if 'ulearn5.nomines' in installed:
            JSONproperties = api.portal.get_tool(name='portal_properties').nomines_properties
            if not JSONproperties.getProperty('nominas_folder_name'):
                return '#'
            else:
                nominas_folder_name = JSONproperties.getProperty('nominas_folder_name').lower()
                path = '/'.join(api.portal.get().getPhysicalPath()) + '/' + nominas_folder_name
                if not api.user.is_anonymous():
                    current = api.user.get_current()
                    roles = api.user.get_roles(username=current.id, obj=path)
                    if 'Manager' in roles or 'Gestor Nomines' in roles:
                        return nominas_folder_name
                return False


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
            if INewsItemFolder.providedBy(obj):
                self.folder_type = 'news'
                break
            if ICommunity.providedBy(obj):
                self.folder_type = 'stream'
                break

    def show_news(self):
        community = self.get_community()
        return community.show_news

    def show_events(self):
        community = self.get_community()
        return community.show_events

    def bubble_class(self, bubble):
        community = self.get_community()
        if community.show_news and community.show_events:
            width = 'col-xs-3'
        elif community.show_news or community.show_events:
            width = 'col-xs-4'
        else:
            width = 'col-xs-6'

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

    def get_links(self):
        current = api.user.get_current()
        language = current.getProperty('language')
        if not language:
            lt = api.portal.get_tool(name='portal_languages')
            language = lt.getPreferredLanguage()

        links = {}
        if language == 'ca':
            links['contact'] = 'https://www.upc.edu/ca/contacte'
            links['sitemap'] = 'https://www.upc.edu/ca/sitemap'
            links['accessibility'] = 'https://www.upc.edu/ca/avis-legal/accessibilitat'
            links['disclaimer'] = 'https://www.upc.edu/ca/avis-legal'
        elif language == 'es':
            links['contact'] = 'https://www.upc.edu/es/contacto'
            links['sitemap'] = 'https://www.upc.edu/es/sitemap'
            links['accessibility'] = 'https://www.upc.edu/es/aviso-legal/accesibilidad'
            links['disclaimer'] = 'https://www.upc.edu/es/aviso-legal'
        else:
            links['contact'] = 'https://www.upc.edu/en/contact'
            links['sitemap'] = 'https://www.upc.edu/en/sitemap'
            links['accessibility'] = 'https://www.upc.edu/en/disclaimer/accessibility'
            links['disclaimer'] = 'https://www.upc.edu/en/disclaimer'

        return links

    def _createLinksFooter(self, language):
        """ Genera el footer segun el idioma que tenga definido el
            usuario en su perfil
        """
        portal = api.portal.get()
        if 'gestion' in portal and 'footer' in portal['gestion'] and language in portal['gestion']['footer']:
            catalog = api.portal.get_tool(name='portal_catalog')
            portalPath = '/'.join(api.portal.get().getPhysicalPath())
            path = portalPath + '/gestion/footer/' + language

            pages = catalog.searchResults(portal_type='Document',
                                          review_state=('published', 'intranet'),
                                          path={'query': path, 'depth': 1},
                                          sort_on='getObjPositionInParent')
            if len(pages) > 0:
                return pages[0].getObject().text
            else:
                return None
        else:
            return None

    def get_customized_footer(self):
        """ Devuelve el footer segun el idioma que tenga definido el
            usuario en su perfil
        """
        if api.user.is_anonymous():
            pass
        else:
            current = api.user.get_current()
            user_language = current.getProperty('language')
            if not user_language or user_language == '':
                lt = api.portal.get_tool(name='portal_languages')
                user_language = lt.getPreferredLanguage()
                current.setMemberProperties({'language': user_language})

            portal = api.portal.get()
            soup_header = get_soup('footer_soup', portal)
            exist = [r for r in soup_header.query(Eq('id_footersoup', user_language))]

            if not exist:
                dades = self._createLinksFooter(user_language)
                record = Record()
                record.attrs['id_footersoup'] = user_language
                record.attrs['dades'] = dades
                soup_header.add(record)
                soup_header.reindex()
                result = dades
            else:
                result = exist[0].attrs['dades']

            return result


class angularRouteView(viewletBase):
    grok.name('ulearn.angularrouteview')
    grok.template('angularrouteview')
    grok.viewletmanager(IAboveContent)
    grok.layer(IUlearn5ThemeLayer)

    def render_viewlet(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True
        return False


class popupNotify(viewletBase):
    grok.name('ulearn.popupNotify')
    grok.template('popup_notify')
    grok.viewletmanager(IPortalFooter)
    grok.layer(IUlearn5ThemeLayer)

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def viewPopup(self):
        if api.portal.get_registry_record('ulearn5.core.controlpopup.IPopupSettings.activate_notify'):
            user = api.user.get_current()
            portal = getSite()
            soup = get_soup('notify_popup', portal)
            user_soup = [r for r in soup.query(Eq('id', user.id))]
            if not user_soup:
                portal = api.portal.get()
                try:
                    return 'notify' in portal['gestion']['popup']
                except:
                    pass
        return False

    def content(self):
        user = api.user.get_current()
        map = {
            'fullname': user.getProperty('fullname', user.id),
        }

        portal = api.portal.get()
        try:
            return portal['gestion']['popup']['notify'].text.raw % map
        except:
            return portal['gestion']['popup']['notify'].text.raw


class popupNotifyBirthday(viewletBase):
    grok.name('ulearn.popupNotifyBirthday')
    grok.template('popup_notify_birthday')
    grok.viewletmanager(IPortalFooter)
    grok.layer(IUlearn5ThemeLayer)

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def viewPopup(self):
        if api.portal.get_registry_record('ulearn5.core.controlpopup.IPopupSettings.activate_birthday'):
            return bool(self.request.cookies.get('popup_birthday', ''))
        return False

    def content(self):
        user = api.user.get_current()
        birthday = user.getProperty('birthday')
        if "/" in birthday:
            birthday = ddatetime.strptime(birthday, '%d/%m/%Y')
        elif "-" in birthday:
            birthday = ddatetime.strptime(birthday, '%d-%m-%Y')

        user_year = int(birthday.strftime('%Y'))
        current_year = int(datetime.datetime.now().strftime('%Y'))

        map = {
            'fullname': user.getProperty('fullname', user.id),
            'years': current_year - user_year
        }

        portal = api.portal.get()
        try:
            return portal['gestion']['popup']['birthday'].text.raw % map
        except:
            return portal['gestion']['popup']['birthday'].text.raw
