import time
import urllib
import transaction
from datetime import datetime
from dateutil.relativedelta import relativedelta

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject


class TestStreamView(FunctionalTestCase):
    members = (
        ('secret', 'Scott Tiger', 'scott@tiger.com', ['members'], '2013-09-24'),
        ('secret', 'Johann Sebastian Bach', 'johan@bach.com', ['members'], '2013-09-24'),)

    def test_check(self):
        return
        # vnc-stream-check no longer exists
        browser = self.login()

        browser.open(self.portal_url + '/@@vnc-stream-check')
        self.assertIn('vncStreamItem', browser.contents)
        self.assertIn('vncStreamItemBody', browser.contents)
        self.assertIn('<div class="vncStreamItemDesc">Welcome to Plone</div>', browser.contents)

        obj = createObject(self.portal, 'Document', 'test_doc', 
                           title='A title',
                           description='Some description',
                           text='Some text')

        browser.open(self.portal_url + '/@@vnc-stream-check')
        self.assertIn('vncStreamItem', browser.contents)
        self.assertIn('vncStreamItemBody', browser.contents)
        self.assertIn('<div class="vncStreamItemDesc">Welcome to Plone</div>', browser.contents)

        self.assertIn('vncStreamItem', browser.contents)
        self.assertIn('vncStreamItemBody', browser.contents)
        self.assertIn('<div class="vncStreamItemDesc">A title</div>', browser.contents)

        date_after_month = datetime.today() + relativedelta(months=1)
        date_test = date_after_month - relativedelta(days=1)
        obj = createObject(self.portal, 'Document', 'test_doc2', 
                           object_date=date_after_month,
                           title='A title 2',
                           description='Some description 2',
                           text='Some text 2')

        browser.open(self.portal_url + '/@@vnc-stream-check',
                     urllib.urlencode({'since': str(date_test)}))
        self.assertIn('vncStreamItem', browser.contents)
        self.assertIn('vncStreamItemBody', browser.contents)
        self.assertIn('<div class="vncStreamItemDesc">A title 2</div>', browser.contents)
        self.assertNotIn('<div class="vncStreamItemDesc">A title</div>', browser.contents)
        self.assertNotIn('<div class="vncStreamItemDesc">Welcome to Plone</div>', browser.contents)

        browser.open(self.portal_url + '/@@vnc-stream-check',
                     urllib.urlencode({'till': str(date_test)}))
        self.assertIn('<div class="vncStreamItemDesc">A title</div>', browser.contents)
        self.assertNotIn('<div class="vncStreamItemDesc">A title 2</div>', browser.contents)

    def test_stream(self):
        return
        # vnc-stream no longer exists
        browser = self.login()

        browser.open(self.portal_url + '/@@vnc-stream')
        self.assertIn('<ul class="vncStreamTabs">', browser.contents)
        self.assertIn('Welcome to Plone', browser.contents)
        self.assertNotIn('A title', browser.contents)

        obj = createObject(self.portal, 'Document', 'test_doc', 
                           title='A title',
                           description='Some description',
                           text='Some text')
        browser.open(self.portal_url + '/@@vnc-stream')
        self.assertIn('A title', browser.contents)
