# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import datetime
from datetime import timedelta

from plone import api
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import construct_calendar
from plone.app.event.base import first_weekday
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.event.base import localized_today
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.app.portlets.portlets import base
from plone.dexterity.interfaces import IDexterityContent
from plone.event.interfaces import IEvent
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from ulearn5.core.content.community import ICommunity
from ulearn5.core.interfaces import IEventsFolder
from ulearn5.theme import calmodule

import itertools


PLMF = MessageFactory('plonelocales')
PRIORITY_TYPES = ['Organizative', 'Closed', 'Open']


class ICalendarPortlet(IPortletDataProvider):
    """ A portlet which renders the calendar portlet """


class Assignment(base.Assignment):
    implements(ICalendarPortlet)
    title = _(u'Calendar')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('templates/calendar.pt')

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

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

        community_path = self.getCommunityPath()
        path = community_path if community_path else path

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

    def getPriorityClassTypeEvent(self, events):
        classType = {'Organizative': 'event-organizative', 'Closed': 'event-closed', 'Open': 'event-open'}
        for typeCommunity in PRIORITY_TYPES:
            for event in events:
                if IEvent.providedBy(event):
                    community = event.aq_parent.aq_parent
                else:
                    community = event.aq_parent.aq_parent.aq_parent
                if community.community_type == typeCommunity:
                    return classType[typeCommunity]

    def getclasstag_event(self, day):
        # Returns class color to show in the calendar
        classtag = ''

        if day['events']:
            # if len(day['events']) > 1:
            if len(day['events']) > 1:
                classtag += ' ' + self.getPriorityClassTypeEvent(day['events'])
                classtag += ' event-multiple '
            else:
                event = day['events'][0]
                community = event.aq_parent.aq_parent.community_type

                if 'Closed' in community:
                    classtag += ' event-closed '
                elif 'Open' in community:
                    classtag += ' event-open '
                else:
                    # Organizative
                    classtag += ' event-organizative '
        return classtag

    def getCalendarDict(self):
        context = aq_inner(self.context)
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
        events = get_events(context,
                            start=start-timedelta(days=30), end=end,
                            ret_mode=RET_MODE_OBJECTS,
                            expand=True, **query_kw)
        return construct_calendar(events, start=start, end=end)

    @property
    def cal_data(self):
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]
        cal_dict = self.getCalendarDict()

        # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
        caldata = [[]]
        for dat in monthdates:
            if len(caldata[-1]) == 7:
                caldata.append([])
            date_events = None
            isodat = dat.isoformat()
            if isodat in cal_dict:
                date_events = cal_dict[isodat]

            caldata[-1].append(
                {'date': dat,
                 'day': dat.day,
                 'month': dat.month,
                 'year': dat.year,
                 'prev_month': dat.month < month,
                 'next_month': dat.month > month,
                 'today':
                    dat.year == today.year and
                    dat.month == today.month and
                    dat.day == today.day,
                 'date_string': u"%s-%s-%s" % (dat.year, dat.month, dat.day),
                 'events': date_events}
            )
        return caldata

    def today(self):
        today = {}
        loc_today = localized_today(self.context)
        weekday = loc_today.isoweekday()
        today['weekdayLit'] = PLMF(self._ts.day_msgid(
            0 if weekday == 7 else weekday, format='l'))
        today['day'] = loc_today.day
        today['month'] = loc_today.month
        today['year'] = loc_today.year
        return today

    @memoize_contextless
    def get_nearest_today_event(self):
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        now = localized_now()
        portal = getToolByName(context, 'portal_url').getPortalObject()

        query = {
            'portal_type': 'Event',
            'review_state': self.state,
            'end': {'query': now, 'range': 'min'},
            'sort_on': 'start',
            'path': '/'.join(portal.getPhysicalPath()) + self.search_base,
            'sort_limit': 1
        }

        result = pc(**query)
        if result:
            return result[0]

    def getEventCalendarDict(self, event):
        start = event.start.strftime('%d/%m') if not event.recurrence else event.ocstart.strftime('%d/%m')
        searchStart = event.start.strftime('%m/%s') if not event.recurrence else event.ocstart.strftime('%m/%s')
        end = event.end.strftime('%d/%m') if not event.recurrence else event.ocend.strftime('%d/%m')
        end = None if end == start else end
        return dict(Title=event.title,
                    getURL=event.absolute_url(),
                    start=start,
                    searchStart=searchStart,
                    end=end,
                    community_type=event.community_type,
                    community_name=event.aq_parent.aq_parent.title,
                    community_url=event.aq_parent.aq_parent.absolute_url())

    def getDayEvents(self, date):
        events = self.getCalendarDict()
        list_events = []
        if date.strftime('%Y-%m-%d') in events:
            events = self.filterOccurrenceEvents(events[date.strftime('%Y-%m-%d')])
            for event in events:
                list_events.append(self.getEventCalendarDict(event))
        return list_events

    def getNextThreeEvents(self):
        context = aq_inner(self.context)
        query_kw = {}
        if self.search_base:
            portal = getToolByName(context, 'portal_url').getPortalObject()
            query_kw['path'] = {'query': '%s%s' % (
                '/'.join(portal.getPhysicalPath()), self.search_base)}

        if self.state:
            query_kw['review_state'] = self.state

        events = get_events(context, ret_mode=RET_MODE_OBJECTS, expand=True, **query_kw)
        events = self.filterNextEvents(events)
        events = self.filterOccurrenceEvents(events)

        list_events = []
        for event in events[:3]:
            list_events.append(self.getEventCalendarDict(event))

        return list_events

    def filterOccurrenceEvents(self, events):
        filter_events = []
        for event in events:
            if not IEvent.providedBy(event):
                ocurrence = event
                event = event.aq_parent
                if event not in filter_events:
                    event.ocstart = ocurrence.start
                    event.ocend = ocurrence.end
                    filter_events.append(event)
            else:
                filter_events.append(event)

        return filter_events

    def filterNextEvents(self, events):
        filter_events = []
        for event in events:
            if event.end > localized_now():
                filter_events.append(event)
        return filter_events

    def getDayEventsGroup(self):
        group_events = []
        if 'day' not in self.request.form and 'month' in self.request.form:
            return None

        if 'day' not in self.request.form and 'month' not in self.request.form:
            list_events = self.getNextThreeEvents()
        else:
            list_events = self.getDayEvents(self.getDateEvents())

        if len(list_events):
            list_events = sorted(list_events, key=lambda x: x['community_name'])
            for communityType in PRIORITY_TYPES:
                for key, group in itertools.groupby(list_events, key=lambda x: x['community_name']):
                    events = [event for event in group]
                    events = sorted(events, key=lambda x: (x['searchStart'], x['Title']))
                    if events[0]['community_type'] == communityType:
                        group_events.append(dict(Title=key,
                                                 getURL=events[0]['getURL'],
                                                 community_url=events[0]['community_url'],
                                                 community_type=events[0]['community_type'],
                                                 community_name=events[0]['community_name'],
                                                 num_events=len(events),
                                                 events=events))
            return group_events
        else:
            return None

    def getDateEvents(self):
        formatDate = "%Y-%m-%d"
        if 'day' in self.request.form:
            date = '{}-{}-{}'.format(self.request.form['year'], self.request.form['month'], self.request.form['day'])
        else:
            date = datetime.today().strftime(formatDate)
        dateEvent = datetime.strptime(date, formatDate)
        return dateEvent

    def show_newevent_url(self):
        """ Assume that the calendar is only shown on the community itself. """
        if IPloneSiteRoot.providedBy(self.context):
            return False
        elif ICommunity.providedBy(self.context):
                user_roles = api.user.get_roles(
                    username=self.username, obj=self.context)
                if 'Editor' in user_roles:
                    return True
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
        if 'community' in self.request.form:
            if self.request.form['community'] != 'False':
                return True

        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True

        return False

    def getCommunityPath(self):
        if self.is_community():
            if 'community_path' in self.request.form:
                return self.request.form['community_path']
            else:
                community = aq_inner(self.context)
                portal = api.portal.get()
                portal_path = portal.getPhysicalPath()
                for obj in aq_chain(community):
                    if ICommunity.providedBy(obj):
                        community_path = obj.getPhysicalPath()
                return '/' + '/'.join(set(community_path) - set(portal_path))
        else:
            return ''

    def get_event_folder_url(self):
        """ Assume that the new event button is only shown on the community itself. """
        context = aq_inner(self.context)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        return '/'.join(portal.getPhysicalPath()) + self.search_base + '/events'


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
