import json
import urllib
import transaction

from zope.component import getUtility

from plone.portlets.interfaces import IPortletType

from Products.Five.testbrowser import Browser

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject


class TestLikeView(FunctionalTestCase):
    members = (
        ('secret', 'Scott Tiger', 'scott@tiger.com', ['members'], '2013-09-24'),
        ('secret', 'Johann Sebastian Bach', 'johan@bach.com', ['members'], '2013-09-24'),)

    def test_you_know_you_like_it(self):
        browser = self.login()
        browser.open(self.portal_url + '/@@you-know-you-like-it')
        self.assertIn("We don't like ambiguity around here. Check yo self before you wreck yo self.", browser.contents)

        obj = createObject(self.portal, 'Document', 'test_doc', 
                           title='A title',
                           description='Some description',
                           text='Some text')
        obj.portal_workflow.doActionFor(
            obj, "publish", comment="publised programmatically")

        browser.open(obj.absolute_url())
        self.assertIn('<span class="thumbs-up">', browser.contents)
        self.assertIn('<span class="thumbs-down">', browser.contents)
        self.assertIn('<span class="tally-total">0</span> likes', browser.contents)
        self.assertIn('<span class="tally-total">0</span> dislikes', browser.contents)
        self.assertIn('class="allowMultiSubmit like-button"', browser.contents)
        self.assertIn('class="allowMultiSubmit dislike-button"', browser.contents)

        browser.getControl(name='form.lovinit').click()
        data = json.loads(browser.contents)
        self.assertTrue(data['downs'] == 0)
        self.assertTrue(data['ups'] == 1)

        browser.open(obj.absolute_url())
        self.assertIn('<span class="thumbs-up selected">', browser.contents)
        self.assertIn('<span class="thumbs-down">', browser.contents)
        self.assertIn('<span class="tally-total">1</span> likes', browser.contents)
        self.assertIn('<span class="tally-total">0</span> dislikes', browser.contents)
        self.logout(browser)

        browser = self.login('scott@tiger.com', 'secret')
        browser.open(obj.absolute_url())
        print browser.contents
        browser.getControl(name='form.lovinit').click()
        browser.open(obj.absolute_url())
        print browser.contents
        # self.assertIn('wizardContentArea', browser.contents)
