# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from ulearn5.theme.testing import ULEARN5_THEME_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that ulearn5.theme is properly installed."""

    layer = ULEARN5_THEME_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ulearn5.theme is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'ulearn5.theme'))

    def test_browserlayer(self):
        """Test that IUlearn5ThemeLayer is registered."""
        from ulearn5.theme.interfaces import (
            IUlearn5ThemeLayer)
        from plone.browserlayer import utils
        self.assertIn(IUlearn5ThemeLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ULEARN5_THEME_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ulearn5.theme'])

    def test_product_uninstalled(self):
        """Test if ulearn5.theme is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'ulearn5.theme'))

    def test_browserlayer_removed(self):
        """Test that IUlearn5ThemeLayer is removed."""
        from ulearn5.theme.interfaces import \
            IUlearn5ThemeLayer
        from plone.browserlayer import utils
        self.assertNotIn(IUlearn5ThemeLayer, utils.registered_layers())
