# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.interface import implements

from ulearn5.core import _


class IFolderViewPortlet(IPortletDataProvider):
    """ A portlet which renders the folder view """

    name = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of the portlet.'),
        required=False
    )

    form.widget(
        'folder',
        RelatedItemsFieldWidget,
        pattern_options={
            "rootPath": "/",
            "mode": "auto",
        }
    )
    folder = schema.Choice(
        title=u"Carpeta",
        source=CatalogSource(is_folderish=True),
        required=True,
    )


class Assignment(base.Assignment):
    implements(IFolderViewPortlet)

    def __init__(self, name="", folder=None):
        self.name = name
        self.folder = folder

    @property
    def title(self):
        if self.name:
            return self.name
        return _(u'Folder View Portlet')



class Renderer(base.Renderer):

    render = ViewPageTemplateFile('folderview.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def title(self):
        return self.data.name if self.data.name else None

    def getItemPropierties(self):
        all_items = []

        nElements = 2
        llistaElements = []

        catalog = api.portal.get_tool(name='portal_catalog')
        container = catalog.searchResults(UID=self.data.folder)

        if container:
            path = container[0].getObject().getPhysicalPath()
            path = "/".join(path)
            items = catalog.searchResults(path={'query': path, 'depth': 1},
                                        sort_on="getObjPositionInParent")


            all_items += [{'item_title': item.Title,
                        'item_desc': item.Description[:110],
                        'item_type': item.portal_type,
                        'item_url': item.getURL(),
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
                       'item_url': item2.getURL(),
                       'item_state': item2.review_state
                       } for item2 in items if item2.exclude_from_nav is False]
        return all_items


class AddForm(base.AddForm):
    schema = IFolderViewPortlet
    label = _(u"Add Folder view Portlet")
    description = _(u"This portlet displays a folder view.")

    def create(self, data):
        return Assignment(name=data.get('name', ""),
                          folder=data.get('folder', None))


class EditForm(base.EditForm):
    schema = IFolderViewPortlet
    label = _(u"Edit Folder view Portlet")
    description = _(u"This portlet displays a folder view.")
