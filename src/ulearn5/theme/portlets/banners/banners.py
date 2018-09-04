# -*- coding: utf-8 -*-
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

import transaction


class TypesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        types = []
        types.append(SimpleVocabulary.createTerm(u'Global', 'Global', _(u'Global')))
        types.append(SimpleVocabulary.createTerm(u'Personal', 'Personal', _(u'Personal')))
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
        else:
            return _(u'banners_personal', default=u'Banners (Personal)')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('banners.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

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

    def createPersonalBannerFolder(self, userid):
        portal = getSite()
        perFolder = self.createOrGetObject(portal['Members'], userid, userid, u'privateFolder')
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

        banFolder = self.createOrGetObject(perFolder, 'banners', 'Banners', u'Folder')
        banFolder.exclude_from_nav = False
        banFolder.setLayout('folder_listing')
        behavior = ISelectableConstrainTypes(banFolder)
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(('ulearn.banner',))
        behavior.setImmediatelyAddableTypes(('ulearn.banner',))

    def getBanners(self):
        catalog = api.portal.get_tool(name='portal_catalog')

        if self.data.typePortlet == 'Personal':
            username = api.user.get_current().id
            path = '/'.join(api.portal.get().getPhysicalPath()) + "/Members/" + username + "/banners"
            portal = api.portal.get()
            if 'Members' in portal:
                if username in portal['Members']:
                    if 'banners' not in portal['Members'][username]:
                        self.createPersonalBannerFolder(username)
                else:
                    self.createPersonalBannerFolder(username)
        else:
            path = '/'.join(api.portal.get().getPhysicalPath()) + "/gestion/banners"

        result = catalog(portal_type='ulearn.banner',
                         review_state='intranet',
                         path={'query': path, 'depth': 1},
                         sort_on="getObjPositionInParent")
        banners = [banner.getObject() for banner in result]
        return banners


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
