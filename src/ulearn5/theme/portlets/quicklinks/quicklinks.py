# from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.portlets import PloneMessageFactory as _PMF
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import CatalogSource
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements

from ulearn5.core import _


class IQuicklinksPortlet(IPortletDataProvider):

    folder = schema.Choice(title=_PMF(u"label_navigation_root_path", default=u"Root node"),
                           description=_PMF(u'help_navigation_root',
                           default=u"You may search for and choose a folder to act as the root of the navigation tree. Leave blank to use the Plone site root."),
                           required=True,
                           source=CatalogSource(is_folderish=True))


class Assignment(base.Assignment):
    implements(IQuicklinksPortlet)

    def __init__(self, folder=None):
        self.folder = folder

    @property
    def title(self):
        """ Display the name in portlet mngmt interface """
        return _(u'Quicklinks')


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('quicklinks.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def getLinks(self):
        res = {}

        portal = getSite()
        instance_name = "/".join(portal.getPhysicalPath())

        catalog = getToolByName(portal, 'portal_catalog')
        folders = catalog.searchResults(portal_type=('Folder', 'privateFolder'),
                                        UID=self.data.folder)

        for brainFolder in folders:
            folder = brainFolder.id
            folderContents = catalog.searchResults(portal_type=('Link', 'Folder', 'privateFolder'),
                                                   path={'query': brainFolder.getPath(), 'depth': 1},
                                                   sort_on='getObjPositionInParent')
            res[folder] = {}
            for brain in folderContents:
                brain = brain.getObject()
                if brain.portal_type == 'Link':
                    url = brain.remoteUrl.replace('${portal_url}', instance_name)
                    res[folder][brain.id] = {'title': brain.title,
                                             'url': url,
                                             'target': '_blink' if brain.open_link_in_new_window else '',
                                             'isLink': True}
                else:
                    res[folder][brain.id] = {'title': brain.title,
                                             'UID': brain.UID(),
                                             'isLink': False}

                    pathNextFolder = brainFolder.getPath() + '/' + brain.id
                    nextFolderContents = catalog.searchResults(portal_type=('Link'),
                                                               path={'query': pathNextFolder, 'depth': 1},
                                                               sort_on='getObjPositionInParent')
                    res[folder][brain.id]['links'] = []
                    for nextBrain in nextFolderContents:
                        nextBrain = nextBrain.getObject()
                        url = nextBrain.remoteUrl.replace('${portal_url}', instance_name)
                        res[folder][brain.id]['links'].append({'title': nextBrain.title,
                                                               'target': '_blink' if nextBrain.open_link_in_new_window else '',
                                                               'url': url})
        return res

    def getInfoFolders(self):
        res = {}
        current = api.user.get_current().id
        catalog = getToolByName(getSite(), 'portal_catalog')
        folders = catalog.searchResults(portal_type=('Folder', 'privateFolder'),
                                        UID=self.data.folder)
        for brainFolder in folders:
            folder = brainFolder.getObject()
            roles = api.user.get_roles(username=current, obj=brainFolder)
            url = brainFolder.getURL() if 'Editor' in roles or 'Contributor' in roles or 'WebMaster' in roles or 'Manager' in roles else None
            res[folder.id] = {'title': folder.title,
                              'url': url,
                              'UID': folder.UID()}

        return res


class AddForm(base.AddForm):
    schema = IQuicklinksPortlet
    label = _(u"Add Quicklinks Portlet")
    description = _(u"This portlet displays quicklinks.")

    def create(self, data):
        return Assignment(folder=data.get('folder', None))


class EditForm(base.EditForm):
    schema = IQuicklinksPortlet
    label = _(u"Edit Quicklinks Portlet")
    description = _(u"This portlet displays quicklinks.")
