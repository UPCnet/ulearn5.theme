# -*- coding: utf-8 -*-
import json
import pkg_resources
import pytz
import scss
import csv
import transaction

from plone import api
from Acquisition import aq_inner
from DateTime import DateTime
from five import grok
from operator import itemgetter
from repoze.catalog.query import Eq
from scss import Scss
from souper.interfaces import ICatalogFactory
from souper.soup import get_soup
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import Interface
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from plone.app.contenttypes.browser.collection import CollectionView
from plone.app.users.browser.userdatapanel import UserDataPanel

from plone.batching import Batch
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import createContentInContainer
from plone.namedfile import NamedBlobFile
from plone.memoize import ram
from plone.memoize.view import memoize_contextless
from plone.protect import createToken
from plone.registry.interfaces import IRegistry

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote_plus

from base5.core.utils import abrevia
from base5.core.utils import abreviaPlainText
from base5.core.utils import json_response
from base5.core.utils import pref_lang

from mrs5.max.utilities import IMAXClient

from ulearn5.core.browser.searchuser import searchUsersFunction
from ulearn5.core.browser.setup import createOrGetObject
from ulearn5.core.content.community import ICommunityACL
from ulearn5.core.controlpanel import IUlearnControlPanelSettings
from ulearn5.core.hooks import packages_installed
from ulearn5.theme.interfaces import IUlearn5ThemeLayer

from email import Encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from cStringIO import StringIO
from zope.i18n import translate
from hashlib import sha1


order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5}

# iCal header and footer
ICS_HEADER = """\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Plone.org//NONSGML plone.app.event//EN
X-WR-TIMEZONE:%(timezone)s
"""

ICS_FOOTER = """\
END:VCALENDAR
"""

# iCal event
ICS_EVENT_START = """\
BEGIN:VEVENT
SUMMARY:%(summary)s
DTSTART;TZID=%(timezone)s;VALUE=DATE-TIME:%(startdate)s
DTEND;TZID=%(timezone)s;VALUE=DATE-TIME:%(enddate)s
DTSTAMP;VALUE=DATE-TIME:%(dtstamp)s
UID:%(uid)s
"""

ICS_EVENT_END = """\
CONTACT:%(contact_name)s\, %(contact_email)s
CREATED;VALUE=DATE-TIME:%(created)s
LAST-MODIFIED;VALUE=DATE-TIME:%(modified)s
LOCATION:%(location)s
URL:%(url)s
END:VEVENT
"""

# iCal timezone
ICS_TIMEZONE_START = """\
BEGIN:VTIMEZONE
TZID:%(timezone)s
X-LIC-LOCATION:%(timezone)s
"""

ICS_TIMEZONE_END = """\
END:VTIMEZONE
"""

# iCal standard
ICS_STANDARD = """\
BEGIN:STANDARD
DTSTART;VALUE=DATE-TIME:20161030T020000
TZNAME:CET
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
END:STANDARD
"""

ATTENDEES_MESSAGE_TEMPLATE = """\
Us han convidat a l'esdeveniment: %(title)s
que comença a les %(start_hour)s del dia %(start_day)s
i acaba a les %(end_hour)s del dia %(end_day)s

"""

ATTENDEES_MESSAGE_TEMPLATE_LOCATION = """\
Que tindrà lloc a: %(location)s
"""

ATTENDEES_MESSAGE_TEMPLATE_ZOOM = """\
Unir-se amb Zoom: %(zoom_link)s
"""

ATTENDEES_MESSAGE_TEMPLATE_END = """\
Assistents: %(attendees)s
Descripció: %(description)s

S'adjunta un fitxer iCalendar amb més informació sobre l'esdeveniment.
"""

ATTENDEES_MESSAGE_TEMPLATE_ES = """\
Ha sido invitado/a al evento: %(title)s
que empieza a las %(start_hour)s del día %(start_day)s
y acaba a las %(end_hour)s del día %(end_day)s

"""

ATTENDEES_MESSAGE_TEMPLATE_LOCATION_ES = """\
Que tendrá lugar en: %(location)s
"""

ATTENDEES_MESSAGE_TEMPLATE_ZOOM_ES = """\
Unirse con Zoom: %(zoom_link)s
"""

ATTENDEES_MESSAGE_TEMPLATE_END_ES = """\
Asistentes: %(attendees)s
Descripción: %(description)s

Se adjunta un archivo iCalendar con más información sobre el evento.
"""

ATTENDEES_MESSAGE_TEMPLATE_EN = """\
You have been invited to the following event: %(title)s
that starts at %(start_hour)s on %(start_day)s
and ends at %(end_hour)s on %(end_day)s

"""

ATTENDEES_MESSAGE_TEMPLATE_LOCATION_EN = """\
That have been place at: %(location)s
"""

ATTENDEES_MESSAGE_TEMPLATE_ZOOM_EN = """\
Join with Zoom: %(zoom_link)s
"""

ATTENDEES_MESSAGE_TEMPLATE_END_EN = """\
Attendees: %(attendees)s
Description: %(description)s

An iCalendar file with more information about the event is attached.
"""


def _render_cachekey(method, self, main_color, secondary_color, background_property, background_color,
                     buttons_color_primary, buttons_color_secondary, maxui_form_bg,
                     alt_gradient_start_color, alt_gradient_end_color, color_community_closed, color_community_organizative, color_community_open):
    """Cache by the specific colors"""
    return (main_color, secondary_color, background_property, background_color,
            buttons_color_primary, buttons_color_secondary, maxui_form_bg,
            alt_gradient_start_color, alt_gradient_end_color,
            color_community_closed, color_community_organizative, color_community_open)


class baseCommunities(grok.View):
    grok.baseclass()

    def update(self):
        self.username = api.user.get_current().id
        self.portal_url = api.portal.get().absolute_url()

    @memoize_contextless
    def portal(self ):
        return getSite()

    def get_all_communities(self):
        pc = api.portal.get_tool('portal_catalog')
        r_results_organizative = pc.searchResults(portal_type="ulearn.community", community_type=u"Organizative", sort_on="sortable_title")
        r_results_closed= pc.searchResults(portal_type="ulearn.community", community_type=u"Closed", sort_on="sortable_title")
        ur_results_open = pc.unrestrictedSearchResults(portal_type="ulearn.community", community_type=u"Open", sort_on="sortable_title")
        return r_results_organizative + r_results_closed + ur_results_open

    def get_authenticator(self):
        return createToken()


class AllCommunities(baseCommunities):
    """ The list of communities """
    grok.context(IPloneSiteRoot)
    grok.require('base.member')
    grok.layer(IUlearn5ThemeLayer)


class communitiesAJAX(baseCommunities):
    """ The list of communities via AJAX """
    grok.name('my-communities-ajax')
    grok.context(IPloneSiteRoot)
    grok.require('base.member')
    grok.template('my_communities_ajax')
    grok.layer(IUlearn5ThemeLayer)


class dynamicCSS(grok.View):
    grok.name('dynamic.css')
    grok.context(Interface)
    grok.layer(IUlearn5ThemeLayer)

    def update(self):
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IUlearnControlPanelSettings)

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        self.request.response.addHeader('Cache-Control', 'must-revalidate, max-age=0, no-cache, no-store')
        if self.settings.main_color and self.settings.secondary_color and \
           self.settings.background_property and \
           self.settings.background_color and \
           self.settings.buttons_color_primary and \
           self.settings.buttons_color_secondary and \
           self.settings.maxui_form_bg and \
           self.settings.alt_gradient_start_color and \
           self.settings.alt_gradient_end_color and \
           self.settings.color_community_closed and \
           self.settings.color_community_organizative and \
           self.settings.color_community_open:
            return '@import "{}/ulearncustom.css";\n'.format(api.portal.get().absolute_url()) + \
                   self.compile_scss(main_color=self.settings.main_color,
                                     secondary_color=self.settings.secondary_color,
                                     background_property=self.settings.background_property,
                                     background_color=self.settings.background_color,
                                     buttons_color_primary=self.settings.buttons_color_primary,
                                     buttons_color_secondary=self.settings.buttons_color_secondary,
                                     maxui_form_bg=self.settings.maxui_form_bg,
                                     alt_gradient_start_color=self.settings.alt_gradient_start_color,
                                     alt_gradient_end_color=self.settings.alt_gradient_end_color,
                                     color_community_closed=self.settings.color_community_closed,
                                     color_community_organizative=self.settings.color_community_organizative,
                                     color_community_open=self.settings.color_community_open)

        else:
            return '@import "{}/ulearncustom.css";'.format(api.portal.get().absolute_url())

    @ram.cache(_render_cachekey)
    def compile_scss(self, **kwargs):
        ulearnthemeegg = pkg_resources.get_distribution('ulearn5.theme')
        scssfile = open('{}/ulearn5/theme/theme/assets/stylesheets/dyn/dynamic.scss'.format(ulearnthemeegg.location))

        settings = dict(main_color=self.settings.main_color,
                        secondary_color=self.settings.secondary_color,
                        background_property=self.settings.background_property,
                        background_color=self.settings.background_color,
                        buttons_color_primary=self.settings.buttons_color_primary,
                        buttons_color_secondary=self.settings.buttons_color_secondary,
                        maxui_form_bg=self.settings.maxui_form_bg,
                        alt_gradient_start_color=self.settings.alt_gradient_start_color,
                        alt_gradient_end_color=self.settings.alt_gradient_end_color,
                        color_community_closed=self.settings.color_community_closed,
                        color_community_organizative=self.settings.color_community_organizative,
                        color_community_open=self.settings.color_community_open)

        variables_scss = """

        $main-color: {main_color};
        $secondary-color: {secondary_color};
        $background-property: {background_property};
        $background-color: {background_color};
        $buttons-color-primary: {buttons_color_primary};
        $buttons-color-secondary: {buttons_color_secondary};
        $maxui-form-bg: {maxui_form_bg};
        $alt-gradient-start-color: {alt_gradient_start_color};
        $alt-gradient-end-color: {alt_gradient_end_color};
        $color_community_closed: {color_community_closed};
        $color_community_organizative: {color_community_organizative};
        $color_community_open: {color_community_open};

        """.format(**settings)

        scss.config.LOAD_PATHS = [
            '{}/ulearn5/theme/theme/assets/stylesheets/bootstrap/'.format(ulearnthemeegg.location)
        ]

        css = Scss(scss_opts={
                   'compress': False,
                   'debug_info': False,
                   })

        dynamic_scss = ''.join([variables_scss, scssfile.read()])

        return css.compile(dynamic_scss)


class CustomCSS(grok.View):
    grok.name('ulearncustom.css')
    grok.context(Interface)
    grok.layer(IUlearn5ThemeLayer)

    index = ViewPageTemplateFile('views_templates/ulearncustom.css.pt')

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        return self.index()


class SearchUser(grok.View):
    grok.name('searchUser')
    grok.context(Interface)
    grok.require('base.member')

    @json_response
    def render(self):
        return {'users': self.get_my_users(),
                'properties': self.get_user_info_for_display()}

    def get_my_users(self):
        searchby = ''
        if len(self.request.form) > 0:
            searchby = self.request.form['search']
        elif 'search' in self.request:
            searchby = self.request.get('search')
        resultat = searchUsersFunction(self.context, self.request, searchby)

        return resultat

    def get_user_info_for_display(self):
        user_properties_utility = getUtility(ICatalogFactory, name='user_properties')

        rendered_properties = []
        extender_name = api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender')
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            for prop in extended_user_properties_utility.directory_properties:
                rendered_properties.append(dict(
                    name=prop,
                    icon=extended_user_properties_utility.directory_icons[prop]
                ))
            return rendered_properties
        else:
            # If it's not extended, then return the simple set of data we know
            # about the user using also the directory_properties field
            for prop in user_properties_utility.directory_properties:
                rendered_properties.append(dict(
                    name=prop,
                    icon=user_properties_utility.directory_icons[prop]
                ))
            return rendered_properties


class searchUsers(grok.View):
    grok.name('searchUsers')
    grok.context(Interface)
    grok.require('base.member')
    grok.layer(IUlearn5ThemeLayer)

    def render(self):
        return 'searchUsers'

    def get_people_literal(self):
        return api.portal.get_registry_record(name='ulearn5.core.controlpanel.IUlearnControlPanelSettings.people_literal')


class ULearnPersonalPreferences(UserDataPanel):
    """
        Override original personal preferences to disable right column portlet
    """

    def __init__(self, context, request):
        super(ULearnPersonalPreferences, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', True)


class TypeAheadSearch(grok.View):
    grok.name('gw_type_ahead_search')
    grok.context(Interface)
    grok.layer(IUlearn5ThemeLayer)

    def render(self):
        # We set the parameters sent in livesearch using the old way.
        q = self.request['q']
        cf = self.request['cf']
        limit = 10
        path = None
        if cf != '':
            path = cf
        ploneUtils = api.portal.get_tool(name='plone_utils')
        portal_url = api.portal.get_tool(name='portal_url')()
        pretty_title_or_id = ploneUtils.pretty_title_or_id
        portalProperties = api.portal.get_tool(name='portal_properties')
        siteProperties = getattr(portalProperties, 'site_properties', None)
        useViewAction = []
        if siteProperties is not None:
            useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

        # SIMPLE CONFIGURATION
        MAX_TITLE = 40
        MAX_DESCRIPTION = 80

        # generate a result set for the query
        catalog = self.context.portal_catalog

        friendly_types = ploneUtils.getUserFriendlyTypes()

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        multispace = u'\u3000'.encode('utf-8')
        for char in ('?', '-', '+', '*', multispace):
            q = q.replace(char, ' ')
        r = q.split()
        r = " AND ".join(r)
        r = quote_bad_chars(r) + '*'
        searchterms = url_quote_plus(r)

        params = {'SearchableText': r,
                  'portal_type': friendly_types,
                  'sort_limit': limit + 1}

        if path is None:
            # useful for subsides
            params['path'] = getNavigationRoot(self.context)
        else:
            params['path'] = path

        params["Language"] = pref_lang()
        # search limit+1 results to know if limit is exceeded
        results = catalog(**params)

        REQUEST = self.context.REQUEST
        RESPONSE = REQUEST.RESPONSE
        RESPONSE.setHeader('Content-Type', 'application/json')

        label_show_all = _('label_show_all', default='Show all items')

        ts = api.portal.get_tool(name='translation_service')

        queryElements = []

        if results:
            # TODO: We have to build a JSON with the desired parameters.
            for result in results[:limit]:
                # Calculate icon replacing '.' per '-' as '.' in portal_types break CSS
                icon = result.portal_type.lower().replace(".", "-")
                itemUrl = result.getURL()
                if result.portal_type in useViewAction:
                    itemUrl += '/view'

                full_title = safe_unicode(pretty_title_or_id(result))
                if len(full_title) > MAX_TITLE:
                    display_title = ''.join((full_title[:MAX_TITLE], '...'))
                else:
                    display_title = full_title

                full_title = full_title.replace('"', '&quot;')

                display_description = safe_unicode(result.Description)
                if len(display_description) > MAX_DESCRIPTION:
                    display_description = ''.join(
                        (display_description[:MAX_DESCRIPTION], '...'))

                # We build the dictionary element with the desired parameters and we add it to the queryElements array.
                queryElement = {'class': '', 'title': display_title, 'description': display_description, 'itemUrl': itemUrl, 'icon': icon}
                queryElements.append(queryElement)

            if len(results) > limit:
                # We have to add here an element to the JSON in case there is too many elements.
                searchquery = '/@@search?SearchableText=%s&path=%s' \
                    % (searchterms, params['path'])
                too_many_results = {'class': 'with-separator', 'title': ts.translate(label_show_all, context=REQUEST), 'description': '', 'itemUrl': portal_url + searchquery, 'icon': ''}
                queryElements.append(too_many_results)

        return json.dumps(queryElements)


class FilteredContentsSearchView(grok.View):
    """ Filtered content search view for every folder. """
    grok.name('filtered_contents_search_view')
    grok.context(Interface)
    grok.require('base.member')
    grok.template('filtered_contents_search')
    grok.layer(IUlearn5ThemeLayer)

    def update(self):
        self.query = self.request.form.get('q', '')
        if self.request.form.get('t', ''):
            self.tags = [v for v in self.request.form.get('t').split(',')]
        else:
            self.tags = []

    def get_batched_contenttags(self, query=None, batch=True, b_size=10, b_start=0):
        pc = api.portal.get_tool(name="portal_catalog")
        path = self.context.getPhysicalPath()
        path = "/".join(path)
        r_results = pc.searchResults(path=path,
                                     sort_on='sortable_title',
                                     sort_order='ascending')

        items_favorites = self.marca_favoritos(r_results)
        items_nofavorites = self.exclude_favoritos(r_results)

        items = self.ordenar_results(items_favorites, items_nofavorites)

        batch = Batch(items, b_size, b_start)
        return batch

    def get_contenttags_by_query(self):
        pc = api.portal.get_tool(name="portal_catalog")
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        if not self.query and not self.tags:
            return self.getContent()

        if not self.query == '':
            multispace = u'\u3000'.encode('utf-8')
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query) + '*'

            if self.tags:
                r_results = pc.searchResults(path=path,
                                             SearchableText=query,
                                             Subject={'query': self.tags, 'operator': 'and'},
                                             sort_on='sortable_title',
                                             sort_order='ascending')
            else:
                r_results = pc.searchResults(path=path,
                                             SearchableText=query,
                                             sort_on='sortable_title',
                                             sort_order='ascending')

            items_favorites = self.marca_favoritos(r_results)
            items_nofavorites = self.exclude_favoritos(r_results)

            items = self.ordenar_results(items_favorites, items_nofavorites)

            return items
        else:
            r_results = pc.searchResults(path=path,
                                         Subject={'query': self.tags, 'operator': 'and'},
                                         sort_on='sortable_title',
                                         sort_order='ascending')

            items_favorites = self.marca_favoritos(r_results)
            items_nofavorites = self.exclude_favoritos(r_results)

            items = self.ordenar_results(items_favorites, items_nofavorites)

            return items

    def get_tags_by_query(self):
        pc = api.portal.get_tool(name="portal_catalog")

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        if not self.query == '':
            multispace = u'\u3000'.encode('utf-8')
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query)
            path = self.context.absolute_url_path()

            r_results = pc.searchResults(path=path,
                                         Subject=query,
                                         sort_on='sortable_title',
                                         sort_order='ascending')

            items_favorites = self.marca_favoritos(r_results)
            items_nofavorites = self.exclude_favoritos(r_results)

            items = self.ordenar_results(items_favorites, items_nofavorites)

            return items
        else:
            return self.get_batched_contenttags(query=None, batch=True, b_size=10, b_start=0)

    def get_container_path(self):
        return self.context.absolute_url()

    def getContent(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        r_results_parent = catalog.searchResults(path={'query': path, 'depth': 1},
                                                 sort_on='sortable_title',
                                                 sort_order='ascending')

        items_favorites = self.favorites_items(path)
        items_nofavorites = self.exclude_favoritos(r_results_parent)

        items = self.ordenar_results(items_favorites, items_nofavorites)

        return items

    def ordenar_results(self, items_favorites, items_nofavorites):
        """ Ordena los resultados segun el tipo (portal_type)
            segun este orden: (order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5})
            y devuelve el diccionario con los favoritos y no favoritos. """
        items_favorites_by_tipus = sorted(items_favorites, key=lambda item: item['tipus'])
        items_nofavorites_by_tipus = sorted(items_nofavorites, key=lambda item: item['tipus'])

        items = [dict(favorite=items_favorites_by_tipus,
                      nofavorite=items_nofavorites_by_tipus)]
        return items

    def marca_favoritos(self, r_results):
        """ De los resultados obtenidos devuelve una lista con los que son FAVORITOS y le asigna un valor al tipus
            segun este orden: (order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5}) """
        current_user = api.user.get_current().id
        favorite = []
        favorite = [{'obj': r, 'tipus': order_by_type[r.portal_type] if r.portal_type in order_by_type else 6} for r in r_results if current_user in r.favoritedBy]

        return favorite

    def exclude_favoritos(self, r_results):
        """ De los resultados obtenidos devuelve una lista con los que NO son FAVORITOS y le asigna un valor al tipus
            segun este orden: (order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5}) """
        current_user = api.user.get_current().id
        nofavorite = []
        for r in r_results:
            if current_user not in r.favoritedBy:
                if r.portal_type in order_by_type:
                    nofavorite += [{'obj': r, 'tipus': order_by_type[r.portal_type]}]
                else:
                    if r.portal_type == 'CloudFile':
                        included = self.include_cloudfile(r)
                        if included:
                            nofavorite += [{'obj': r, 'tipus': 6}]
                    else:
                        nofavorite += [{'obj': r, 'tipus': 6}]
        #nofavorite = [{'obj': r, 'tipus': order_by_type[r.portal_type] if r.portal_type in order_by_type else 6} for r in r_results if current_user not in r.favoritedBy]
        return nofavorite

    def include_cloudfile(self, obj):
        """ Indica si debemos incluir el objeto del conjunto a retornar.
            Retorna cierto si el objeto es de tipo cloudfile y el usuario
            tiene permisos de edicion sobre la comunidad """
        sm = getSecurityManager()
        return True if sm.checkPermission(ModifyPortalContent, obj.getObject()) else False

    def favorites_items(self, path):
        """ Devuelve todos los favoritos del usuario y le asigna un valor al tipus
            segun este orden: (order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5}) """
        pc = api.portal.get_tool(name='portal_catalog')
        current_user = api.user.get_current().id
        results = pc.searchResults(path={'query': path},
                                   favoritedBy=current_user,
                                   sort_on='sortable_title',
                                   sort_order='ascending')

        favorite = [{'obj': r, 'tipus': order_by_type[r.portal_type] if r.portal_type in order_by_type else 6} for r in results]
        return favorite


class SearchFilteredContentAjax(FilteredContentsSearchView):
    """ Ajax helper for filtered content search view for every folder. """

    grok.name('search_filtered_content')
    grok.context(Interface)
    grok.template('filtered_contents_search_ajax')
    grok.layer(IUlearn5ThemeLayer)


class AllTags(grok.View):
    grok.name('alltags')
    grok.context(Interface)
    grok.template('alltags')
    grok.require('base.authenticated')
    grok.layer(IUlearn5ThemeLayer)

    def get_subscribed_tags(self):
        portal = getSite()
        current_user = api.user.get_current()
        userid = current_user.id

        soup_tags = get_soup('user_subscribed_tags', portal)
        tags_soup = [r for r in soup_tags.query(Eq('id', userid))]

        return tags_soup[0].attrs['tags'] if tags_soup else []

    def get_unsubscribed_tags(self):

        subjects = []
        pc = api.portal.get_tool('portal_catalog')
        subjs_index = pc._catalog.indexes['Subject']
        [subjects.append(index[0]) for index in subjs_index.items()]

        portal = getSite()
        current_user = api.user.get_current()
        userid = current_user.id

        soup_tags = get_soup('user_subscribed_tags', portal)
        tags_soup = [r for r in soup_tags.query(Eq('id', userid))]
        if tags_soup:
            user_tags = tags_soup[0].attrs['tags']
        else:
            user_tags = ()
        return list(set(subjects) - set(user_tags))


class SearchFilteredNews(grok.View):
    """ Filtered news search view for every folder. """

    grok.name('search_filtered_news')
    grok.context(Interface)
    grok.layer(IUlearn5ThemeLayer)

    def render(self):

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        def makeHtmlData(news_list):
            news_html = ''
            current = api.user.get_current()
            lang = current.getProperty('language')
            readmore = translate("readmore", "ulearn", None, None, lang, None)
            if news_list:
                for noticia in news_list:
                    noticiaObj = noticia.getObject()
                    if noticiaObj.text is None:
                        text = ''
                    else:
                        if noticiaObj.description:
                            text = abrevia(noticiaObj.description, 150)
                        else:
                            text = abrevia(noticiaObj.text.raw, 150)

                    news_html += '<li class="noticies clearfix">' \
                                   '<div>' \
                                      '<div class="imatge_noticia">'

                    if noticia.getObject().image:
                        news_html +=     '<img src="' + noticia.getURL() + '/@@images/image/thumb" alt="'+noticiaObj.id + '" title="' + noticiaObj.id + '" class="newsImage" width="222" height="222">'
                    else:
                        news_html +=     '<img class="newsImage" src="/++theme++ulearn5/assets/images/defaultImage.png" width="222" height="222">'

                    news_html +=      '</div>' \
                                      '<div class="text_noticia">' \
                                        '<h2>'\
                                        '<a href="' + noticia.getURL() + '">' + abreviaPlainText(noticia.Title, 70) + '</a>'\
                                        '</h2>'\
                                        '<p><time class="smaller">'+str(noticiaObj.modification_date.day()) + '/' + str(noticiaObj.modification_date.month()) + '/' + str(noticiaObj.modification_date.year())+'</time></p>'\
                                        '<span>'+text+'</span>'\
                                        '<a href="'+noticia.getURL()+'" class="readmore" title="'+abreviaPlainText(noticia.Title, 70) + '"><span class="readmore">'+readmore.encode('utf-8') + '</span>'\
                                        '</a>'\
                                      '</div>'\
                                   '</div>'\
                                 '</li>'
            else:
                news_html = '<li class="noticies clearfix"><div> No hay coincidencias. </div></li>'
            return news_html

        pc = api.portal.get_tool(name="portal_catalog")
        now = DateTime()
        path = self.context.getPhysicalPath()
        path = "/".join(path)
        self.query = self.request.form.get('q', '')
        if not self.query == '':
            multispace = u'\u3000'.encode('utf-8')
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query) + '*'
            r_results = pc.searchResults(portal_type='News Item',
                                         review_state=['intranet', 'published'],
                                         expires={'query': now, 'range': 'min', },
                                         sort_on='created',
                                         sort_order='reverse',
                                         is_outoflist=False,
                                         SearchableText=query
                                         )

            data = makeHtmlData(r_results)
            return data

        else:
            r_results = pc.searchResults(portal_type='News Item',
                                         review_state=['intranet', 'published'],
                                         expires={'query': now, 'range': 'min', },
                                         sort_on='created',
                                         sort_order='reverse',
                                         is_outoflist=False
                                         )

            data = makeHtmlData(r_results)
            return data


class ContentsPrettyView(grok.View):
    """ Show content in a pretty way for every folder. """

    grok.name('contents_pretty_view')
    grok.context(Interface)
    grok.require('base.member')
    grok.template('contentspretty')
    grok.layer(IUlearn5ThemeLayer)

    def getItemPropierties(self):
        all_items = []

        catalog = api.portal.get_tool(name='portal_catalog')
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        nElements = 2
        llistaElements = []

        items = catalog.searchResults(path={'query': path, 'depth': 1},
                                      sort_on="getObjPositionInParent")
        all_items += [{'item_title': item.Title,
                       'item_desc': item.Description[:110],
                       'item_type': item.portal_type,
                       'item_url': item.getURL() + '/view',
                       'item_path': item.getPath(),
                       'item_state': item.review_state,
                       } for item in items if item.exclude_from_nav is False]

        if len(all_items) > 0:
            # Retorna una llista amb els elements en blocs de 2 elements
            llistaElements = [all_items[i:i + nElements] for i in range(0, len(all_items), nElements)]
        return llistaElements

    def getBlocs(self):
        llistaElements = self.getItemPropierties()
        return len(llistaElements)

    def getSubItemPropierties(self, item_path):
        all_items = []
        catalog = api.portal.get_tool(name='portal_catalog')
        path = item_path

        items = catalog.searchResults(path={'query': path, 'depth': 1},
                                      sort_on="getObjPositionInParent")
        all_items += [{'item_title': item2.Title,
                       'item_desc': item2.Description[:120],
                       'item_type': item2.portal_type,
                       'item_url': item2.getURL() + '/view',
                       'item_state': item2.review_state
                       } for item2 in items if item2.exclude_from_nav is False]
        return all_items


class CollectionNewsView(grok.View, CollectionView):
    """ Show content from news in a folder, added search input """

    grok.name('collection_news_view')
    grok.context(Interface)
    grok.require('base.member')
    grok.template('collectionnews')
    grok.layer(IUlearn5ThemeLayer)

    def viewUrl(self):
        return self.context.absolute_url()

    def lastSearch(self):
        if 'filter' in self.request.form:
            return self.request.form['filter']
        else:
            return ''

    def results(self, **kwargs):
        contentFilter = dict(self.request.get('contentFilter', {}))
        contentFilter.update(kwargs.get('contentFilter', {}))

        if 'filter' in self.request.form:
            queryFilters = ''
            for fil in self.context.query:
                if fil['i'] == 'SearchableText':
                    queryFilters = fil['v']

            formFilter = self.request.form['filter']
            filters = formFilter if queryFilters == '' else queryFilters.encode('utf-8') + ' ' + formFilter
            contentFilter.update({'SearchableText': filters})

        kwargs.setdefault('custom_query', contentFilter)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)
        results = self.collection_behavior.results(**kwargs)
        return results

    def abreviaText(self, text, num):
        return abrevia(text, num)


class SharedWithMe(baseCommunities):
    """ The list of communities """

    grok.context(IPloneSiteRoot)
    grok.require('base.member')
    grok.layer(IUlearn5ThemeLayer)


class ResetMenuBar(grok.View):
    """ This view reset the personal bar """
    grok.name('reset_menu')
    grok.context(Interface)
    grok.require('base.webmaster')
    grok.layer(IUlearn5ThemeLayer)

    def render(self):
        portal = api.portal.get_tool(name='portal_url').getPortalObject()
        soup_menu = get_soup('menu_soup', portal)
        soup_menu.clear()
        self.redirect(portal.absolute_url())

class ResetHeader(grok.View):
    """ This view reset the header """
    grok.name('reset_header')
    grok.context(Interface)
    grok.require('base.webmaster')
    grok.layer(IUlearn5ThemeLayer)

    def render(self):
        portal = api.portal.get_tool(name='portal_url').getPortalObject()
        soup_header = get_soup('header_soup', portal)
        soup_header.clear()
        self.redirect(portal.absolute_url())

class ResetFooter(grok.View):
    """ This view reset the footer """
    grok.name('reset_footer')
    grok.context(Interface)
    grok.require('base.webmaster')
    grok.layer(IUlearn5ThemeLayer)

    def render(self):
        portal = api.portal.get_tool(name='portal_url').getPortalObject()
        soup_footer = get_soup('footer_soup', portal)
        soup_footer.clear()
        self.redirect(portal.absolute_url())

class SendEventToAttendees(grok.View):
    grok.context(IDexterityContent)
    grok.name('event_to_attendees')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IUlearn5ThemeLayer)

    def render(self):
        portal = api.portal
        mailhost = api.portal.get_tool(name='MailHost')

        map = {
            'title': self.context.Title(),
            'start_hour': self.applytz(self.context.start).strftime('%H:%M:%S'),
            'start_day': self.applytz(self.context.start).strftime('%d/%m/%Y'),
            'end_hour': self.applytz(self.context.end).strftime('%H:%M:%S'),
            'end_day': self.applytz(self.context.end).strftime('%d/%m/%Y'),
            'attendees': ', '.join(self.context.attendees).encode('utf-8'),
            'description': self.context.Description()
        }

        location = self.context.location is not None and self.context.location != ""
        if location:
            map.update({'location': self.context.location.encode('utf-8')})

        installed = packages_installed()
        zoom_link = 'ulearn5.zoom' in installed and hasattr(self.context, 'url_zoom') and self.context.url_zoom is not None

        if zoom_link:
            map.update({'zoom_link': self.context.url_zoom.encode('utf-8')})

        default_language = api.portal.get_default_language()

        if default_language == 'ca':
            body = ATTENDEES_MESSAGE_TEMPLATE % map

            if location:
                body += ATTENDEES_MESSAGE_TEMPLATE_LOCATION % map

            if zoom_link:
                body += ATTENDEES_MESSAGE_TEMPLATE_ZOOM % map

            body += ATTENDEES_MESSAGE_TEMPLATE_END % map
            subject = 'Invitació: %s\n' % self.context.Title()

        elif default_language == 'es':
            body = ATTENDEES_MESSAGE_TEMPLATE_ES % map
            if location:
                body += ATTENDEES_MESSAGE_TEMPLATE_LOCATION_ES % map

            if zoom_link:
                body += ATTENDEES_MESSAGE_TEMPLATE_ZOOM_ES % map

            body += ATTENDEES_MESSAGE_TEMPLATE_END_ES % map
            subject = 'Invitación: %s\n' % self.context.Title()

        else:
            body = ATTENDEES_MESSAGE_TEMPLATE_EN % map
            if location:
                body += ATTENDEES_MESSAGE_TEMPLATE_LOCATION_EN % map

            if zoom_link:
                body += ATTENDEES_MESSAGE_TEMPLATE_ZOOM_EN % map

            body += ATTENDEES_MESSAGE_TEMPLATE_END_EN % map
            subject = 'Meeting: %s\n' % self.context.Title()

        msg = MIMEMultipart()
        msg['From'] = portal.get_registry_record('plone.email_from_address')
        msg['To'] = ', '.join(self.context.attendees).encode('utf-8')
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = Header(subject, 'utf-8')

        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        msg.attach(self.get_ics())
        mailhost.send(msg)

    def get_ics(self):
        """iCalendar output
        """
        out = StringIO()

        out.write(ICS_HEADER % {'timezone': api.portal.get_registry_record('plone.portal_timezone')})
        out.write(self.getICal())
        out.write(ICS_FOOTER)

        part = MIMEBase('application', "octet-stream")
        part.set_payload(self.n2rn(out.getvalue()))
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s.ics"' % self.context.getId())

        return part

    def getICal(self):
        """get iCal data
        """
        portal = api.portal
        out = StringIO()

        map = {
            'summary': self.vformat(self.context.Title()),
            'timezone': portal.get_registry_record('plone.portal_timezone'),
            'startdate': self.rfc2445dtlocal(self.context.start),
            'enddate': self.rfc2445dtlocal(self.context.end),
            'dtstamp': self.rfc2445dt(DateTime()),
            'uid': self.context.sync_uid,
        }
        out.write(ICS_EVENT_START % map)

        for assistant in self.context.attendees:
            out.write('ATTENDEE;CN={0};ROLE=REQ-PARTICIPANT:{0}\n'.format(assistant.encode('utf-8')))

        for category in self.context.subject:
            out.write('CATEGORIES:%s\n' % category.encode('utf-8'))

        contact_name = self.context.contact_name.encode('utf-8') if self.context.contact_name else None
        location = self.context.location.encode('utf-8') if self.context.location else None
        map = {
            'contact_name': contact_name,
            'contact_email': self.context.contact_email,
            'created': self.rfc2445dt(self.context.creation_date),
            'modified': self.rfc2445dt(self.context.modification_date),
            'location': location,
            'url': self.context.absolute_url(),
        }
        out.write(ICS_EVENT_END % map)

        map = {
            'timezone': portal.get_registry_record('plone.portal_timezone'),
        }
        out.write(ICS_TIMEZONE_START % map)

        out.write(ICS_STANDARD)
        out.write(ICS_TIMEZONE_END)

        return out.getvalue()

    def vformat(self, s):
        # return string with escaped commas and semicolons
        # NOTE: RFC 2445 specifies "a COLON character in a 'TEXT' property value
        # SHALL NOT be escaped with a BACKSLASH character." So watch out for
        # non-TEXT values, should they be introduced later in this code!
        return s.strip().replace(', ', '\, ').replace(';', '\;')

    def n2rn(self, s):
        return s.replace('\n', '\r\n')

    def rfc2445dt(self, dt):
        # return UTC in RFC2445 format YYYYMMDDTHHMMSSZ
        return dt.HTML4().replace('-', '').replace(':', '')

    def rfc2445dtlocal(self, dt):
        # return UTC in RFC2445 format YYYYMMDDTHHMMSS
        return self.applytz(dt).strftime('%Y%m%dT%H%M%S')

    def applytz(self, dt):
        return dt.astimezone(pytz.timezone(api.portal.get_registry_record('plone.portal_timezone')))


class UsersCommunities(grok.View):
    """ Vista que dado un usuario devuelve las comunidades a las que esta susbcrito y con que rol
        o dada una comunidad devuelve los usuarios susbcritos y con que rol
    """

    grok.name('users_communities')
    grok.context(IPloneSiteRoot)
    grok.require('base.webmaster')
    grok.template('users_communities')
    grok.layer(IUlearn5ThemeLayer)

    def result(self):
        result = []

        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        if 'user' in self.request.form:
            user_id = self.request.form['user']
            communities_subscription = maxclient.people[user_id].subscriptions.get()
            user = api.user.get(userid=user_id)
            if user:
                fullname = user.getProperty('fullname', '-')
                fullname = fullname if fullname else '-'

            for community in communities_subscription:
                if 'delete' in community['permissions']:
                    role = 'owner'
                elif 'write' in community['permissions']:
                    role = 'writer'
                elif 'read' in community['permissions']:
                    role = 'reader'
                listUsers = []
                listUsers.append({'id': user.id,
                                  'fullname': fullname,
                                  'role': role})
                result.append({'title': community['displayName'],
                               'users': sorted(listUsers, key=itemgetter('fullname'))})

        if 'idcommunity' in self.request.form:
            community_id = self.request.form['idcommunity']
            data = {'portal_type': "ulearn.community",
                    'sort_on': 'sortable_title',
                    'id': community_id }

            pc = api.portal.get_tool(name='portal_catalog')
            communities = pc.unrestrictedSearchResults(**data)

            maxclient, settings = getUtility(IMAXClient)()
            maxclient.setActor(settings.max_restricted_username)
            maxclient.setToken(settings.max_restricted_token)

            for community in communities:
                communityObj = community._unrestrictedGetObject()
                community_hash = sha1(communityObj.absolute_url()).hexdigest()
                users_subscription = maxclient.contexts[community_hash].subscriptions.get(qs={'limit': 0})
                listUsers = []
                if users_subscription:
                    for user_subscription in users_subscription:
                        user = api.user.get(userid=user_subscription['username'])
                        if user:
                            fullname = user.getProperty('fullname', '-')
                            fullname = fullname if fullname else '-'
                            if 'delete' in user_subscription['permissions']:
                                role = 'owner'
                            elif 'write' in user_subscription['permissions']:
                                role = 'writer'
                            elif 'read' in user_subscription['permissions']:
                                role = 'reader'
                            listUsers.append({'id': user.id,
                                              'fullname': fullname,
                                              'role': role})
                result.append({'title': communityObj.title,
                               'users': sorted(listUsers, key=itemgetter('fullname'))})

        return result

    # Funcion antigua con grupos
    # def result(self):
    #     result = []

    #     if 'user' in self.request.form or 'idcommunity' in self.request.form:
    #         data = {'portal_type': "ulearn.community",
    #                 'sort_on': 'sortable_title'}

    #         if 'idcommunity' in self.request.form:
    #             data.update({'id': self.request.form['idcommunity']})

    #         pc = api.portal.get_tool(name='portal_catalog')
    #         communities = pc.searchResults(**data)

    #         for community in communities:
    #             info = ICommunityACL(community.getObject())().attrs.get('acl', '')

    #             listUsers = []
    #             if 'users' in info:
    #                 for tmpuser in info['users']:
    #                     user = api.user.get(userid=tmpuser['id'])
    #                     if user:
    #                         fullname = user.getProperty('fullname', '-')
    #                         fullname = fullname if fullname else '-'
    #                         if 'user' not in self.request.form or self.request.form['user'] == user.id:
    #                             listUsers.append({'id': user.id,
    #                                               'fullname': fullname,
    #                                               'role': tmpuser['role']})

    #             if 'groups' in info:
    #                 for group in info['groups']:
    #                     users = api.user.get_users(groupname=group['id'])
    #                     for user in users:
    #                         if 'user' not in self.request.form or self.request.form['user'] == user.id:
    #                             fullname = user.getProperty('fullname', '-')
    #                             fullname = fullname if fullname else '-'
    #                             listUsers.append({'id': user.id,
    #                                               'fullname': fullname + ' [' + group['id'].encode('utf-8') + ']',
    #                                               'role': group['role']})

    #             if listUsers:
    #                 result.append({'id': community.id,
    #                                'title': community.Title,
    #                                'users': sorted(listUsers, key=itemgetter('fullname'))})

    #     return result

    def allCommunities(self):
        data = {'portal_type': "ulearn.community",
                'sort_on': 'sortable_title'}
        pc = api.portal.get_tool(name='portal_catalog')
        communities = pc.searchResults(**data)

        result = []
        for community in communities:
            result.append({'id': community.id,
                           'title': community.Title})
        return result

    def showResults(self):
        return 'user' in self.request.form or 'idcommunity' in self.request.form

    def userSearch(self):
        return 'user' in self.request.form


class ExportUsersCommunities(grok.View):
    grok.name('export_users_communities')
    grok.context(IPloneSiteRoot)
    grok.require('base.webmaster')

    data_header_columns = [
        "User ID",
        "Fullname",
        "Email",
        "Community",
        "Role"]

    def render(self):
        try:
            output_file = StringIO()
            # Write the BOM of the text stream to make its charset explicit
            output_file.write(u'\ufeff'.encode('utf8'))
            self.write_data(output_file)

            portal = getSite()
            exports = createOrGetObject(portal['gestion'], 'exports', u'Exports', u'privateFolder')
            exports.exclude_from_nav = False
            exports.setLayout('folder_listing')
            behavior = ISelectableConstrainTypes(exports)
            behavior.setConstrainTypesMode(1)
            behavior.setLocallyAllowedTypes(('File',))
            behavior.setImmediatelyAddableTypes(('File',))
            exports._Delete_objects_Permission = ('Site Administrator','Manager',)

            file_filename = u'export_users_communities.csv'
            file = NamedBlobFile(data=output_file.getvalue(), contentType='text/csv', filename=file_filename)

            if file_filename not in exports:
                export = createContentInContainer(exports, 'File', title=file_filename, file=file)
                api.content.transition(obj=export, transition='reject')
                transaction.commit()
            else:
                export = exports[file_filename]
                export.file = file
                export.reindexObject()

            return 'OK'
        except:
            return 'KO'

    def data(self):
        result = []

        data = {'portal_type': "ulearn.community",
                'sort_on': 'sortable_title'}

        pc = api.portal.get_tool(name='portal_catalog')
        communities = pc.unrestrictedSearchResults(**data)

        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        portal = api.portal.get()
        registry = queryUtility(IRegistry)
        ulearn_settings = registry.forInterface(IUlearnControlPanelSettings)
        if ulearn_settings.url_site != None:
            url_site = ulearn_settings.url_site
        else:
            url_site = portal.absolute_url()

        for community in communities:
            communityObj = community._unrestrictedGetObject()
            community_hash = sha1(url_site + '/' + '/'.join(communityObj.absolute_url().split('/')[-1:])).hexdigest()
            users_subscription = maxclient.contexts[community_hash].subscriptions.get(qs={'limit': 0})
            if users_subscription:
                for user_subscription in users_subscription:
                    user = api.user.get(userid=user_subscription['username'])
                    if user:
                        if 'delete' in user_subscription['permissions']:
                            role = 'owner'
                        elif 'write' in user_subscription['permissions']:
                            role = 'writer'
                        elif 'read' in user_subscription['permissions']:
                            role = 'reader'
                        result.append({'userid': user.id,
                                       'fullname': user.getProperty('fullname', ''),
                                       'email': user.getProperty('email', ''),
                                       'community': community.Title + ' (' + community.id + ')',
                                       'role': role})
        return result

    def write_data(self, output_file):
        writer = csv.writer(output_file, dialect='excel', delimiter=',')
        writer.writerow(self.data_header_columns)

        for row in self.data():
            writer.writerow([row['userid'],
                             row['fullname'],
                             row['email'],
                             row['community'],
                             row['role']])

# Antiguo con grupos
# class ExportUsersCommunities(grok.View):
#     grok.name('export_users_communities')
#     grok.context(IPloneSiteRoot)
#     grok.require('base.webmaster')

#     data_header_columns = [
#         "User ID",
#         "Fullname",
#         "Group",
#         "Community",
#         "Role"]

#     def render(self):
#         try:
#             output_file = StringIO()
#             # Write the BOM of the text stream to make its charset explicit
#             output_file.write(u'\ufeff'.encode('utf8'))
#             self.write_data(output_file)

#             portal = getSite()
#             exports = createOrGetObject(portal['gestion'], 'exports', u'Exports', u'privateFolder')
#             exports.exclude_from_nav = False
#             exports.setLayout('folder_listing')
#             behavior = ISelectableConstrainTypes(exports)
#             behavior.setConstrainTypesMode(1)
#             behavior.setLocallyAllowedTypes(('File',))
#             behavior.setImmediatelyAddableTypes(('File',))
#             exports._Delete_objects_Permission = ('Site Administrator','Manager',)

#             file_filename = u'export_users_communities.csv'
#             file = NamedBlobFile(data=output_file.getvalue(), contentType='text/csv', filename=file_filename)

#             if file_filename not in exports:
#                 export = createContentInContainer(exports, 'File', title=file_filename, file=file)
#                 api.content.transition(obj=export, transition='reject')
#                 transaction.commit()
#             else:
#                 export = exports[file_filename]
#                 export.file = file
#                 export.reindexObject()

#             return 'OK'
#         except:
#             return 'KO'

#     def data(self):
#         result = []

#         data = {'portal_type': "ulearn.community",
#                 'sort_on': 'sortable_title'}

#         pc = api.portal.get_tool(name='portal_catalog')
#         communities = pc.searchResults(**data)

#         for community in communities:
#             info = ICommunityACL(community.getObject())().attrs.get('acl', '')

#             if 'users' in info:
#                 for tmpuser in info['users']:
#                     user = api.user.get(userid=tmpuser['id'])
#                     if user:
#                         result.append({'fullname': user.getProperty('fullname', ''),
#                                        'userid': user.id,
#                                        'group': '',
#                                        'community': community.Title + ' (' + community.id + ')',
#                                        'role': tmpuser['role']})

#             if 'groups' in info:
#                 for group in info['groups']:
#                     users = api.user.get_users(groupname=group['id'])
#                     for user in users:
#                         result.append({'fullname': user.getProperty('fullname', ''),
#                                        'userid': user.id,
#                                        'group': group['id'].encode('utf-8'),
#                                        'community': community.Title + ' (' + community.id + ')',
#                                        'role': group['role']})
#         return result

#     def write_data(self, output_file):
#         writer = csv.writer(output_file, dialect='excel', delimiter=',')
#         writer.writerow(self.data_header_columns)

#         for row in self.data():
#             writer.writerow([row['userid'],
#                              row['fullname'],
#                              row['group'],
#                              row['community'],
#                              row['role']])
