import ast
import urllib
import transaction

from Products.Five.testbrowser import Browser

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject


class TestUtilView(FunctionalTestCase):
    #members = (
    #    ('secret', 'Scott Tiger', 'scott@tiger.com', ['members'], '2013-09-24'),
    #       ('secret', 'Johann Sebastian Bach', 'johan@bach.com', ['members'], '2013-09-24'),)

    def test_is_popup_mode_on(self):
        browser = self.login()
        browser.open(self.portal_url + '/@@is-popup-mode-on')
        self.assertEqual(browser.contents, '')

        browser.open(self.portal_url + '/@@is-popup-mode-on?popup_mode=1')
        self.assertIn('True', browser.contents)

    def test_addcontentarea_viewlet(self):
        browser = self.login()
        obj = createObject(self.portal, 'Document', 'test_doc', 
                           title='A title',
                           description='Some description',
                           text='Some text')
        browser.open(self.portal_url + '/@@addcontentarea_viewlet',
                     urllib.urlencode({'uid': obj.UID()}))
        self.assertIn('wizardContentArea', browser.contents)
        self.assertIn('wizard-steps', browser.contents)
        self.assertIn('step1', browser.contents)
        self.assertIn('step2', browser.contents)
        self.assertIn('step3', browser.contents)

    # def test_search_containers_json(self):
    #     browser = self.login()

    #     obj = createObject(self.portal, 'Document', 'test_doc', 
    #                        title='A title',
    #                        description='Some description',
    #                        text='Some text')

    #     # obj.SearchableText = 'Some description'
    #     # self.catalog.indexObject(obj)
    #     # transaction.commit()

    #     browser.open(self.portal_url + '/@@search-containers.json',
    #                  urllib.urlencode({'term': 'description'}))
    #     self.assertIn('description', browser.contents)

    def test_record_portlet_state(self):
        browser = self.login()

        browser.open(self.portal_url + '/@@record-portlet-state',
                     urllib.urlencode({'hash': '123',
                                       'action': 'close',
                                       'value': '1'}))
        self.assertIn('Done.', browser.contents)

        browser.open(self.portal_url + '/@@record-portlet-state',
                     urllib.urlencode({'hash': '123',
                                       'action': 'close',
                                       'value': '0'}))
        self.assertIn('Done.', browser.contents)

    def test_folder_content_types(self):
        browser = self.login()

        browser.open(self.portal_url + '/@@folder-content-types')
        result = ast.literal_eval(browser.contents)

        types = [t['title'] for t in result]
        self.assertIn('All', types)
        self.assertIn('Folder', types)
        self.assertIn('Page', types)
