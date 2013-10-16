import ast
import urllib
import transaction

from zope.component import getUtility

from plone.portlets.interfaces import IPortletType

from Products.Five.testbrowser import Browser

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject


class TestAutocompleteView(FunctionalTestCase):
    def test_email_autocomplete_json(self):
        browser = self.login()
        # TODO: zimbra mockup?
        #browser.open(self.portal_url + '/@@email_autocomplete_json')
        #print browser.contents
        # self.assertIn('wizardContentArea', browser.contents)
