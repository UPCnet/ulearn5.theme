# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from five import grok
from plone import api
from plone.app.portlets.portlets import base
from plone.dexterity.utils import createContentInContainer
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from ulearn5.core import _
from ulearn5.core.browser.security import execute_under_special_role
from ulearn5.core.content.community import ICommunity

import transaction


class TypesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        types = []
        types.append(SimpleVocabulary.createTerm(u'Global', 'Global', _(u'Global')))
        types.append(SimpleVocabulary.createTerm(u'Personal', 'Personal', _(u'Personal')))
        types.append(SimpleVocabulary.createTerm(u'Comunitat', 'Comunitat', _(u'Comunitat')))
        return SimpleVocabulary(types)


grok.global_utility(TypesVocabulary, name=u"ulearn.portlets.banners.Types")


class IBannersPortlet(IPortletDataProvider):
    """ A portlet which renders the banners portlet """

    typePortlet = schema.Choice(
        title=_(u'Type'),
        vocabulary=u"ulearn.portlets.banners.Types",
        default=u'Global',
        required=True
    )


class Assignment(base.Assignment):
    implements(IBannersPortlet)

    def __init__(self, typePortlet="Global"):
        self.typePortlet = typePortlet

    @property
    def title(self):
        if self.typePortlet == 'Global':
            return _(u'banners_global', default=u'Banners (Global)')
        elif self.typePortlet == 'Personal':
            return _(u'banners_personal', default=u'Banners (Personal)')
        else:
            return _(u'banners_comunitats', default=u'Banners (Comunitats)')


def createOrGetObject(self, context, newid, title, type_name):
        if newid in context.contentIds():
            obj = context[newid]
        else:
            obj = createContentInContainer(context, type_name, title=title, checkConstrains=False)
            transaction.savepoint()
            if obj.id != newid:
                context.manage_renameObject(obj.id, newid)
            obj.reindexObject()
        return obj


def createPersonalBannerFolder(userid):
    portal = getSite()
    perFolder = createOrGetObject(portal, portal['Members'], userid, userid, u'privateFolder')
    perFolder.exclude_from_nav = False
    perFolder.setLayout('folder_listing')
    behavior = ISelectableConstrainTypes(perFolder)
    behavior.setConstrainTypesMode(1)
    behavior.setLocallyAllowedTypes(('Folder',))
    behavior.setImmediatelyAddableTypes(('Folder',))

    api.content.disable_roles_acquisition(perFolder)
    for username, roles in perFolder.get_local_roles():
        perFolder.manage_delLocalRoles([username])
    perFolder.manage_setLocalRoles(userid, ['Contributor', 'Editor', 'Reader'])

    banFolder = createOrGetObject(portal, perFolder, 'banners', 'Banners', u'Folder')
    banFolder.exclude_from_nav = False
    banFolder.setLayout('folder_listing')
    behavior = ISelectableConstrainTypes(banFolder)
    behavior.setConstrainTypesMode(1)
    behavior.setLocallyAllowedTypes(('ulearn.banner',))
    behavior.setImmediatelyAddableTypes(('ulearn.banner',))


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('banners.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def getBanners(self):
        catalog = api.portal.get_tool(name='portal_catalog')

        if self.data.typePortlet == 'Personal':
            username = api.user.get_current().id
            path = '/'.join(api.portal.get().getPhysicalPath()) + "/Members/" + username + "/banners"
            portal = api.portal.get()
            if 'Members' in portal:
                if username in portal['Members']:
                    if 'banners' not in portal['Members'][username]:
                        execute_under_special_role(portal, "Manager", createPersonalBannerFolder, username)
                else:
                    execute_under_special_role(portal, "Manager", createPersonalBannerFolder, username)
        elif self.data.typePortlet == 'Global':
            path = '/'.join(api.portal.get().getPhysicalPath()) + "/gestion/banners"
        else:
            path = self.getCommunityPath()

        data = {'portal_type': 'ulearn.banner',
                'review_state': 'intranet',
                'sort_on': "getObjPositionInParent"}

        if self.data.typePortlet == 'Comunitat':
            data.update({'community_type': ('Open', 'Closed', 'Organizative')})
            data.update({'path': path})
        else:
            data.update({'path': {'query': path, 'depth': 1}})

        result = catalog(**data)
        banners = [banner.getObject() for banner in result]
        return banners

    def getCommunityPath(self):
        community = aq_inner(self.context)
        for obj in aq_chain(community):
            if ICommunity.providedBy(obj):
                return '/' + '/'.join(obj.getPhysicalPath())
        return '/'.join(api.portal.get().getPhysicalPath())


class AddForm(base.AddForm):
    schema = IBannersPortlet
    label = _(u"Add Banners Portlet")
    description = _(u"This portlet displays banners.")

    def create(self, data):
        return Assignment(typePortlet=data.get('typePortlet', "Global"))


class EditForm(base.EditForm):
    schema = IBannersPortlet
    label = _(u"Edit Banners Portlet")
    description = _(u"This portlet displays banners.")
