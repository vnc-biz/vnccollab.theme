import ast
import urllib
import transaction

from Products.Five.testbrowser import Browser

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject


class TestHomepageView(FunctionalTestCase):
    def test_homepage(self):
        browser = self.login()
        browser.open(self.portal_url + '/@@homepage_view')

        self.assertIn('wizardContentArea', browser.contents)
        self.assertIn('wizard-steps', browser.contents)
        self.assertIn('step step1', browser.contents)
        self.assertIn('step step2', browser.contents)
        self.assertIn('ENTER CONTENT INFORMATION', browser.contents)
        self.assertIn('step step3', browser.contents)
        self.assertIn('WHERE DO YOU WANT TO PUT THE NEW ITEM?', browser.contents)
        self.assertIn('wizard-overlay', browser.contents)
        self.assertIn('Loading...', browser.contents)
        self.assertIn('<img width="80" height="80" src="http://nohost/plone/defaultUser.png" alt="test_user_1_" />', browser.contents)
        self.assertIn('<a href="http://nohost/plone/author/test_user_1_">My Profile</a>', browser.contents)
        self.assertIn('<a class="logoutLink" title="Click to logout" href="http://nohost/plone/logout">Log out</a>', browser.contents)
        self.assertIn('portal-breadcrumbs', browser.contents)
        self.assertIn('breadcrumbs-home', browser.contents)
