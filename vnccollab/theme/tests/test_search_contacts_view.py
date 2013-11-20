import ast
import json
import urllib
import transaction

from zope.component import getUtility
from zope.publisher.browser import TestRequest

from plone.portlets.interfaces import IPortletType

from plone.app.testing import TEST_USER_NAME
from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.search_contacts import SearchContacts


class TestSearchContactsView(FunctionalTestCase):
    members = (
        ('secret', 'Scott Tiger', 'scott@tiger.com', ['members'], '2013-09-24'),
        ('secret', 'Scott2 Tiger2', 'scott2@tiger2.com', ['members'], '2013-09-24'),
        ('secret', 'Johann Sebastian Bach', 'johan@bach.com', ['members'], '2013-09-24'),
        ('secret', 'Johann2 Sebastian Bach', 'johan2@bach.com', ['members'], '2013-09-24'),)

    def test_search_contacts(self):
        browser = self.login()
        browser.open(self.portal_url + '/@@search-contacts?q=Micheal')
        data = json.loads(browser.contents)
        self.assertEqual(data, [])

        browser.open(self.portal_url + '/@@search-contacts?q=Sc')
        self.assertTrue(len(browser.contents) == 0)

        browser.open(self.portal_url + '/@@search-contacts?q=Sco')
        data = json.loads(browser.contents)
        self.assertTrue(len(data), 2)
        for idx in range(0,2):
            self.assertTrue(data[idx]['fullname'] in ['Scott Tiger', 'Scott2 Tiger2'])
            self.assertTrue(data[idx]['id'] in ['scott@tiger.com', 'scott2@tiger2.com'])

        browser.open(self.portal_url + '/@@search-contacts?q=Jo')
        self.assertTrue(len(browser.contents) == 0)

        browser.open(self.portal_url + '/@@search-contacts?q=joh')
        data = json.loads(browser.contents)
        self.assertTrue(len(data), 2)
        for idx in range(0,2):
            self.assertTrue(data[idx]['fullname'] in ['Johann Sebastian Bach', 'Johann2 Sebastian Bach'])
            self.assertTrue(data[idx]['id'] in ['johan@bach.com', 'johan2@bach.com'])
