# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from ulearn5.core import _
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import _prepare_range
from plone.app.event.base import first_weekday
from ComputedAttribute import ComputedAttribute
from zExceptions import NotFound
from plone.app.event.portlets import get_calendar_url
from plone.app.event.base import expand_events
from plone.app.event.base import get_events, construct_calendar
from plone.app.event.base import localized_today, localized_now, dt_end_of_day
from plone.app.event.base import start_end_query
from plone.app.event.base import wkday_to_mon1
from plone.app.querystring import queryparser
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.event.interfaces import IEventAccessor
from zope import schema
from zope.component.hooks import getSite
import calendar
import json
from urllib import urlencode

from plone.memoize.view import memoize_contextless
from zope.component import getMultiAdapter
from Acquisition import aq_inner, aq_chain
from ulearn5.core.content.community import ICommunity

from plone.app.event.base import find_ploneroot
from plone.app.event.base import find_site


def get_calendar_url(context):
    # search_base is always from the portal_root object. We won't include
    # the path from the portal root object, so we traverse to the calendar
    # object and call it's url then.
    calendar_url = None
    site_url = find_site(context, as_url=True)
    calendar_url = '%s/event_listing' % site_url

    return calendar_url


try:
    from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection as ICollection  # noqa
    from plone.app.contenttypes.interfaces import IFolder
    search_base_uid_source = CatalogSource(object_provides={
        'query': [
            ICollection.__identifier__,
            IFolder.__identifier__
        ],
        'operator': 'or'
    })
except ImportError:
    search_base_uid_source = CatalogSource(is_folderish=True)
    ICollection = None

PLMF = MessageFactory('plonelocales')


class ICalendarTile(Schema):

    tile_title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Title of the tile"),
        required=True)

    state = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=None,
        required=False,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates")
    )

    search_base_uid = schema.Choice(
        title=_(u'portlet_label_search_base', default=u'Search base'),
        description=_(
            u'portlet_help_search_base',
            default=u'Select search base Folder or Collection to search for '
                    u'events. The URL to to this item will also be used to '
                    u'link to in calendar searches. If empty, the whole site '
                    u'will be searched and the event listing view will be '
                    u'called on the site root.'
        ),
        required=False,
        source=search_base_uid_source,
    )


@implementer(ICalendarTile)
class CalendarTile(Tile):
    """Calendar Tile code is coppied from plone.app.portlet Portlet Calendar
    """

    index = ViewPageTemplateFile('templates/calendari.pt')
    state = None
    search_base = None
    search_base_uid = None

    _search_base = None

    def _uid(self):
        # This is only called if the instance doesn't have a search_base_uid
        # attribute, which is probably because it has an old
        # 'search_base' attribute that needs to be converted.
        path = self.search_base
        portal = getToolByName(self, 'portal_url').getPortalObject()
        try:
            search_base = portal.unrestrictedTraverse(path.lstrip('/'))
        except (AttributeError, KeyError, TypeError, NotFound):
            return
        return search_base.UID()

    search_base_uid = ComputedAttribute(_uid, 1)

    @property
    def search_base(self):
        if not self._search_base:
            self._search_base = uuidToObject(self.data.search_base_uid)
        # aq_inner, because somehow search_base gets wrapped by the renderer
        return aq_inner(self._search_base)

    @property
    def search_base_path(self):
        search_base = self.search_base
        if search_base is not None:
            search_base = '/'.join(search_base.getPhysicalPath())
        return search_base

    def __call__(self):
        context = aq_inner(self.context)
        # self.calendar_url = self.context.absolute_url()
        # self.calendar_url = get_calendar_url(context, self.search_base_path)
        self.calendar_url = get_calendar_url(context)
        # self.calendar_url = 'http://localhost:8080/Plone2/event_listing'

        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = prev_year, prev_month = (
            self.get_previous_month(year, month))
        self.next_year, self.next_month = next_year, next_month = (
            self.get_next_month(year, month))
        self.prev_query = '?month=%s&year=%s' % (prev_month, prev_year)
        self.next_query = '?month=%s&year=%s' % (next_month, next_year)

        self.cal = calendar.Calendar(first_weekday())
        self._ts = getToolByName(context, 'translation_service')
        self.month_name = PLMF(
            self._ts.month_msgid(month),
            default=self._ts.month_english(month)
        )
        # strftime %w interprets 0 as Sunday unlike the calendar.
        strftime_wkdays = [
            wkday_to_mon1(day) for day in self.cal.iterweekdays()
        ]
        self.weekdays = [
            PLMF(self._ts.day_msgid(day, format='s'),
                 default=self._ts.weekday_english(day, format='a'))
            for day in strftime_wkdays
        ]
        return self.index()

    def year_month_display(self):
        """ Return the year and month to display in the calendar.
        """
        context = aq_inner(self.context)
        request = self.request

        # Try to get year and month from request
        year = request.get('year', None)
        month = request.get('month', None)

        # Or use current date
        today = localized_today(context)
        if not year:
            year = today.year
        if not month:
            month = today.month

        # try to transform to number but fall back to current
        # date if this is ambiguous
        try:
            year, month = int(year), int(month)
        except (TypeError, ValueError):
            year, month = today.year, today.month

        return year, month

    def get_previous_month(self, year, month):
        if month == 0 or month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
        return (year, month)

    def get_next_month(self, year, month):
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        return (year, month)

    def date_events_url(self, date):
        return '%s?mode=day&date=%s' % (self.calendar_url, date)

    def cal_data(self):
        """Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)

        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]

        start = monthdates[0]
        end = monthdates[-1]

        data = self.data
        query = {}

        if data['state']:
            query['review_state'] = data['state']

        events = []
        # import ipdb;ipdb.set_trace()
        query.update(self.request.get('contentFilter', {}))
        # search_base = self.search_base
        # search_base = '/Plone2/'
        search_base = "/".join(self.context.getParentNode().getPhysicalPath())


        if ICollection and ICollection.providedBy(search_base):
            # Whatever sorting is defined, we're overriding it.
            query = queryparser.parseFormquery(
                search_base, search_base.query,
                sort_on='start', sort_order=None
            )

            # restrict start/end with those from query, if given.
            if 'start' in query and query['start'] > start:
                start = query['start']
            if 'end' in query and query['end'] < end:
                end = query['end']

            start, end = _prepare_range(search_base, start, end)
            query.update(start_end_query(start, end))
            events = search_base.results(
                batch=False, brains=True, custom_query=query
            )
            events = expand_events(
                events, ret_mode=RET_MODE_OBJECTS,
                start=start, end=end,
                sort='start', sort_reverse=False
            )
        else:
            # search_base_path = self.search_base_path
            # search_base_path = '/Plone2/'
            search_base_path = "/".join(self.context.getParentNode().getPhysicalPath())
            if search_base_path:
                query['path'] = {'query': search_base_path}
            # query['path'] = {'query': '/Plone/ca'}
            events = get_events(context, start=start, end=end,
                                ret_mode=RET_MODE_OBJECTS,
                                expand=True, **query)

        cal_dict = construct_calendar(events, start=start, end=end)

        # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
        caldata = [[]]
        for dat in monthdates:
            if len(caldata[-1]) == 7:
                caldata.append([])
            date_events = None
            isodat = dat.isoformat()
            if isodat in cal_dict:
                date_events = cal_dict[isodat]

            events_string = u""
            if date_events:
                for occ in date_events:
                    accessor = IEventAccessor(occ)
                    # location = accessor.location
                    # whole_day = accessor.whole_day
                    # time = accessor.start.time().strftime('%H:%M')
                    # TODO: make 24/12 hr format configurable
                    # base = u'<a href="%s"><span class="title">%s</span>'\
                    #        u'%s%s%s</a>'
                    base = u'%s'
                    events_string += base % (
                        accessor.title)

            caldata[-1].append(
                {'date': dat,
                 'day': dat.day,
                 'prev_month': dat.month < month,
                 'next_month': dat.month > month,
                 'today':
                    dat.year == today.year and
                    dat.month == today.month and
                    dat.day == today.day,
                 'date_string': u"%s-%s-%s" % (dat.year, dat.month, dat.day),
                 'events_string': events_string,
                 'events': date_events})
        return caldata

    def today(self):
        today = {}
        loc_today = localized_today(self.context)
        weekday = loc_today.isoweekday()
        today['weekday'] = PLMF(self._ts.day_msgid(0 if weekday == 7 else weekday, format='l'))
        today['number'] = loc_today.day
        return today

    @memoize_contextless
    def get_nearest_today_event(self):
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        now = localized_now()

        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        context = aq_inner(self.context)
        path = navigation_root_path

        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                community = aq_inner(obj)
                path = '/'.join(community.getPhysicalPath())

        query = {
            'portal_type': 'Event',
            'review_state': 'intranet',
            'start': {'query': [now, dt_end_of_day(now)], 'range': 'min:max'},
            'end': {'query': now, 'range': 'min'},
            'sort_on': 'start',
            'path': path,
            'sort_limit': 1
        }

        result = pc(**query)
        if result:
            return result[0]
        else:
            return

    def get_next_three_events(self):
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        now = localized_now()

        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        context = aq_inner(self.context)
        path = navigation_root_path
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                community = aq_inner(obj)
                path = '/'.join(community.getPhysicalPath())

        query = {
            'portal_type': 'Event',
            'review_state': 'intranet',
            'end': {'query': now, 'range': 'min'},
            'sort_on': 'start',
            'path': path,
        }

        result = pc(**query)
        nearest = self.get_nearest_today_event()
        if nearest:
            return [event for event in result if event.id != nearest.id][:3]
        else:
            return result[:3]


    def nav_pattern_options(self, query):
        return json.dumps({
            'url': '%s/@@calendari%s&%s' % (
                getSite().absolute_url(),
                query,
                self.quote_query('state', self.data['state'])),
            'target': '.portletCalendar'
        })

    def hash(self):
        return self.request.form.get(
            'portlethash',
            getattr(self, '__portlet_metadata__', {}).get('hash', ''))

    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('tile_title', '')

    def quote_query(self, key, value):
        """ This only is capable of Zope encode tuples. If ever required, can
        be extended to support further types (and complex dicts of data)"""

        if isinstance(value, tuple):
            return ''.join(
                ['{}:tuple={}&'.format(key, item) for item in value])
        else:
            return ''
