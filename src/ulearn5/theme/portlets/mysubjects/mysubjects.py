# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.component import queryUtility
from zope.interface import implements

from ulearn5.core import _
from ulearn5.core.controlpanel import IUlearnControlPanelSettings

import json
import requests


class IMySubjectsPortlet(IPortletDataProvider):
    """ A portlet which can show actived.
    """

    wsUrl = schema.TextLine(title=_(u"label_wsurl", default=u"Webservice Url"),
                            description=_(u"help_wsurl",
                                          default=u"Url on moodle."),
                            default=u"",
                            required=True)

    wsFunction = schema.TextLine(title=_(u"label_wsfunction", default=u"Webservice Function"),
                                 description=_(u"help_wsfunction",
                                               default=u"Function on moodle."),
                                 default=u"",
                                 required=True)

    wsToken = schema.TextLine(title=_(u"label_wstoken", default=u"Webservice Token"),
                              description=_(u"help_wstoken",
                                            default=u"Token to connect to moodle."),
                              default=u"",
                              required=True)


class Assignment(base.Assignment):
    implements(IMySubjectsPortlet)

    title = _(u'mysubjects', default=u'mysubjects')

    def __init__(self, wsUrl="", wsFunction="", wsToken=""):
        self.wsUrl = wsUrl
        self.wsFunction = wsFunction
        self.wsToken = wsToken


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('mysubjects.pt')

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def getSubjects(self):
        """ return list of user subjects to show in portlet """

        mtool = self.context.portal_membership
        userid = mtool.getAuthenticatedMember().id

        payload = {"wstoken": self.data.wsToken,
                   "wsfunction": self.data.wsFunction,
                   "moodlewsrestformat": 'json',
                   "username": userid.lower(),
                   }

        req = requests.post(self.data.wsUrl,
                            data=payload,
                            verify=False)
        try:
            userSubjects = json.loads(req.json())
        except:
            userSubjects = {'studentCourses': [], 'teacherCourses': []}
        return userSubjects

    def getPrimaryColor(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings)
        return settings.main_color


class AddForm(base.AddForm):
    schema = IMySubjectsPortlet
    label = _(u"Add My Subjects Portlet")
    description = _(u"This portlet displays my subjects on moodle.")

    def create(self, data):
        return Assignment(wsUrl=data.get('wsUrl', ''),
                          wsFunction=data.get('wsFunction', ''),
                          wsToken=data.get('wsToken', ''))


class EditForm(base.EditForm):
    schema = IMySubjectsPortlet
    label = _(u"Edit My Subjects Portlet")
    description = _(u"This portlet displays my subjects on moodle.")
