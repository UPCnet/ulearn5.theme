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

    wsUrl = schema.TextLine(title=_("label_wsurl", default="Webservice Url"),
                            description=_("help_wsurl",
                                          default="Url on moodle."),
                            default="",
                            required=True)

    wsFunction = schema.TextLine(title=_("label_wsfunction", default="Webservice Function"),
                                 description=_("help_wsfunction",
                                               default="Function on moodle."),
                                 default="",
                                 required=True)

    wsToken = schema.TextLine(title=_("label_wstoken", default="Webservice Token"),
                              description=_("help_wstoken",
                                            default="Token to connect to moodle."),
                              default="",
                              required=True)


class Assignment(base.Assignment):
    implements(IMySubjectsPortlet)

    title = _('mysubjects', default='mysubjects')

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
    label = _("Add My Subjects Portlet")
    description = _("This portlet displays my subjects on moodle.")

    def create(self, data):
        return Assignment(wsUrl=data.get('wsUrl', ''),
                          wsFunction=data.get('wsFunction', ''),
                          wsToken=data.get('wsToken', ''))


class EditForm(base.EditForm):
    schema = IMySubjectsPortlet
    label = _("Edit My Subjects Portlet")
    description = _("This portlet displays my subjects on moodle.")
