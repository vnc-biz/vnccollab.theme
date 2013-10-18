import os
import sys
import unittest2 as unittest

from zope.publisher.browser import TestRequest

from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from vnccollab.theme.settings import AnonymousHomepageSettingsEditForm as \
    AnonForm

from vnccollab.theme.tests.base import IntegrationTestCase
from vnccollab.theme.testing import VNCCOLLAB_THEME_INTEGRATION_TESTING


class TestAnonymousHomepageSettings(IntegrationTestCase):
    """Tests Anonymous Homepage Settings in Control Panel"""
    layer = VNCCOLLAB_THEME_INTEGRATION_TESTING

    def test_anon_settings_exists(self):
        """Test if there's an Anonymous Homepage Settings in Control Panel."""
        anon_view = self._get_anon_settings_view()
        self.assertTrue(anon_view)

    def test_set_help_url(self):
        """Tests if we can set the Help URL."""
        TEST_URL = 'http://www.google.com'

        anon_form = self._get_anon_settings_form()
        anon_form.applyChanges(dict(help_url=TEST_URL,
                                    delete_logo=False,
                                    logo=None))
        help_url = api.portal.get_registry_record(AnonForm.help_url_key)
        self.assertEqual(TEST_URL, help_url)

    def test_set_logo(self):
        """Test setting and deleting the logo."""
        portal = api.portal.get()
        custom_skin = portal.portal_skins.custom
        anon_form = self._get_anon_settings_form()
        png = file(self._get_my_folder_path('logo.png')).read()

        # Creates and tests the existence of the logo
        anon_form.applyChanges(dict(help_url=None,
                                    delete_logo=False,
                                    logo=png))
        logo = custom_skin.get('logo.png', None)
        self.assertTrue(logo)

        # Deletes the logo
        anon_form.applyChanges(dict(help_url=None,
                                    delete_logo=True,
                                    logo=None))
        logo = custom_skin.get('logo.png', None)
        self.assertFalse(logo)


    def _get_anon_settings_view(self):
        """Gets Anonymous Homepage Settings Form via traverse."""
        return self._traverse('anonhomepage-settings')


    def _get_anon_settings_form(self, request=None):
        """Gets the form behind Anonymous Homepage Settings Form via
        traverse."""
        portal = api.portal.get()
        if request is None:
            request = {}
        anon_form = AnonForm(portal, request)
        return anon_form

    def _traverse(self, path):
        portal = api.portal.get()

        try:
            obj = portal.restrictedTraverse(path)
        except KeyError:
            obj = None

        return obj

    def _get_my_folder_path(self, path=''):
        my_module_path = os.path.abspath(
            sys.modules[self.__class__.__module__].__file__)
        my_folder_path = os.path.dirname(my_module_path)
        if path:
            my_folder_path = os.path.join(my_folder_path, path)
        return my_folder_path


