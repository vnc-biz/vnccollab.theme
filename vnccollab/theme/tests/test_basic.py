import unittest2 as unittest

from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from vnccollab.theme.tests.base import IntegrationTestCase
from vnccollab.theme.testing import VNCCOLLAB_THEME_INTEGRATION_TESTING


class TestBasic(IntegrationTestCase):
    layer = VNCCOLLAB_THEME_INTEGRATION_TESTING

    def test_addon_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'vnccollab.theme'
        qi_tool = api.portal.get_tool(name='portal_quickinstaller')
        installed = [p['id'] for p in qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')
