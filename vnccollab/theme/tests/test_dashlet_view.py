import ast
import urllib
import transaction

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject


class TestDashletView(FunctionalTestCase):
    def test_dashlet(self):
        browser = self.login()
        browser.open(self.portal_url + '/@@dashlet')
        self.assertIn('>Users<', browser.contents)
        self.assertIn('>Events<', browser.contents)
        self.assertIn('>News<', browser.contents)

        browser.open(self.portal_url + '/@@dashlet?type=mails')
        self.assertNotIn('>Users<', browser.contents)
        self.assertNotIn('>Events<', browser.contents)
        self.assertNotIn('>News<', browser.contents)
