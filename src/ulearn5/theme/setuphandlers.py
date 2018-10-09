# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.interfaces import INonInstallable

from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'ulearn5.theme:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def setupVarious(context):
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('ulearn5.theme_various.txt') is None:
        return

    # Sitemap
    registry = queryUtility(IRegistry)
    factory = getUtility(IVocabularyFactory, 'plone.app.vocabularies.ReallyUserFriendlyTypes')
    vocabulary = factory(context)
    nav_properties = registry.forInterface(INavigationSchema, prefix='plone')
    nav_properties.displayed_types = tuple([term.value for term in vocabulary])

    import transaction
    transaction.commit()
