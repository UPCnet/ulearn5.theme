from plone import api
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner, aq_chain
import json
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize.view import memoize_contextless

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _
from ulearn5.core.content.community import ICommunity
from ulearn5.core.interfaces import IEventsFolder
from plone.app.event.base import localized_today, localized_now, dt_end_of_day
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import first_weekday
from plone.app.event.base import get_events, construct_calendar
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.event.interfaces import IEventAccessor
from plone.dexterity.interfaces import IDexterityContent

from DateTime import DateTime
from zope.i18nmessageid import MessageFactory
PLMF = MessageFactory('plonelocales')

from ulearn5.theme import calmodule


class ICalendarPortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(ICalendarPortlet)

    title = _(u'ulearncalendar', default=u'Calendar portlet')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/calendar.pt')

    def update(self):
        context = aq_inner(self.context)

        if IPloneSiteRoot.providedBy(self.context) or \
           not IDexterityContent.providedBy(self.context):
            path = ''
        else:
            if ICommunity.providedBy(aq_inner(self.context)):
                community = aq_inner(self.context)
                portal = api.portal.get()
                portal_path = portal.getPhysicalPath()
                community_path = community.getPhysicalPath()
                path = '/' + '/'.join(set(community_path) - set(portal_path))
            else:
                path = ''
        self.search_base = path
        self.state = ('published', 'intranet')

        self.username = api.user.get_current().id
        # self.user_info = get_safe_member_by_id(self.username)

        self.calendar_url = get_calendar_url(context, self.search_base)

        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = prev_year, prev_month = (
            self.get_previous_month(year, month))
        self.next_year, self.next_month = next_year, next_month = (
            self.get_next_month(year, month))
        # TODO: respect current url-query string
        self.prev_query = '?month=%s&year=%s' % (prev_month, prev_year)
        self.next_query = '?month=%s&year=%s' % (next_month, next_year)

        self.cal = calmodule.Calendar(first_weekday())
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

    def __init__(self, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)

    def nav_pattern_options(self, query):
        return json.dumps({
            'url': '%s/@@calendari%s&%s' % (
                getSite().absolute_url(),
                query,
                self.quote_query('state', self.state)),
            'target': '.portletCalendar'
        })

    def quote_query(self, key, value):
        """ This only is capable of Zope encode tuples. If ever required, can
        be extended to support further types (and complex dicts of data)"""

        if isinstance(value, tuple):
            return ''.join(
                ['{}:tuple={}&'.format(key, item) for item in value])
        else:
            return ''

    @property
    def cal_data(self):
        """Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]

        query_kw = {}
        if self.search_base:
            portal = getToolByName(context, 'portal_url').getPortalObject()
            query_kw['path'] = {'query': '%s%s' % (
                '/'.join(portal.getPhysicalPath()), self.search_base)}

        if self.state:
            query_kw['review_state'] = self.state

        start = monthdates[0]
        end = monthdates[-1]
        events = get_events(context, start=start, end=end,
                            ret_mode=RET_MODE_OBJECTS,
                            expand=True, **query_kw)
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
                    location = accessor.location
                    whole_day = accessor.whole_day
                    time = accessor.start.time().strftime('%H:%M')
                    # TODO: make 24/12 hr format configurable
                    base = u'<a href="%s"><span class="title">%s</span>'\
                           u'%s%s%s</a>'
                    events_string += base % (
                        accessor.url,
                        accessor.title,
                        not whole_day and u' %s' % time or u'',
                        not whole_day and location and u', ' or u'',
                        location and u' %s' % location or u'')

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
            'review_state': self.state,
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
            'review_state': self.state,
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

    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        context = aq_inner(self.context)
        path = navigation_root_path
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                community = aq_inner(obj)
                path = '/'.join(community.getPhysicalPath())

        weeks = self.calendar.getEventsForCalendar(month, year, path=path)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, context=context, request=self.request)]
                    day['eventstring'] = '\n'.join(localized_date + [' %s' %
                        self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)

        return weeks

    def show_newevent_url(self):
        """ Assume that the calendar is only shown on the community itself. """
        context = aq_inner(self.context)
        if IPloneSiteRoot.providedBy(self.context):
            return False
        else:
            user_roles = api.user.get_roles(username=self.username, obj=self.context)
            if 'Editor' in user_roles and ICommunity.providedBy(context):
                return True
            else:
                return False

    def newevent_url(self):
        """ Assume that the new event button is only shown on the community itself. """
        context = aq_inner(self.context)
        # Fist, a light guard
        if ICommunity.providedBy(context):
            event_folder_id = ''
            for obj_id in context.objectIds():
                if IEventsFolder.providedBy(context[obj_id]):
                    event_folder_id = obj_id

            return '{}/{}/++add++Event'.format(context.absolute_url(), event_folder_id)
        else:
            return ''

    def is_community(self):
        """ Assume that the calendar is only shown on the community itself. """
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True

        return False

    def get_event_folder_url(self):
        """ Assume that the new event button is only shown on the community itself. """
        context = aq_inner(self.context)
        return '{}/events'.format(context.absolute_url())


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
