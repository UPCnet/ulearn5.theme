# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import ulearn5.theme


class Ulearn5ThemeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=ulearn5.theme)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ulearn5.theme:default')


ULEARN5_THEME_FIXTURE = Ulearn5ThemeLayer()


ULEARN5_THEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ULEARN5_THEME_FIXTURE,),
    name='Ulearn5ThemeLayer:IntegrationTesting'
)


ULEARN5_THEME_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ULEARN5_THEME_FIXTURE,),
    name='Ulearn5ThemeLayer:FunctionalTesting'
)


ULEARN5_THEME_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        ULEARN5_THEME_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='Ulearn5ThemeLayer:AcceptanceTesting'
)
