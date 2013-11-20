import ast
import json
import urllib
import transaction
from base64 import decodestring
from OFS.Image import File

from plone.app.blob.tests.utils import getFile
from plone.testing.z2 import Browser
from plone.app.blob.tests.utils import makeFileUpload, getImage

from ZPublisher.HTTPRequest import FileUpload

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.util import VNCCollabUtilView


def makeResponse(request):
    """ create a fake request and set up logging of output """
    headers = {}
    output = []
    class Response:
        def setHeader(self, header, value):
            headers[header] = value
        def write(self, msg):
            output.append(msg)
        def redirect(self, url):
            output.append('redirect: %s' % url)
            return url
    request.RESPONSE = Response()
    request.response = Response()
    return headers, output, request


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

    def test_search_containers_json(self):
        browser = self.login()

        obj = createObject(self.portal, 'Folder', 'test_folder', 
                           title='A title',
                           description='Some description',
                           text='Some text')

        browser.open(self.portal_url + '/@@search-containers.json',
                     urllib.urlencode({'term': 'description'}))
        result = json.loads(browser.contents)
        self.assertTrue(len(result) > 0)
        self.assertIn('desc', result[0])
        self.assertIn('description', result[0]['desc'])

    def test_record_portlet_state(self):
        browser = Browser(self.portal)
        browser.open(self.portal_url + '/@@record-portlet-state',
                     urllib.urlencode({'hash': '123',
                                       'action': 'close',
                                       'value': '1'}))
        self.assertIn('error', browser.contents)

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

    def test_uploadFile(self):
        file = File('foo', 'Foo', getFile('plone.pdf'), 'application/pdf')
        file.filename = 'foo.pdf'

        myUpload = makeFileUpload(file, 'test.gif')
        myUpload.method = 'GET'
        view = VNCCollabUtilView(self.portal, myUpload)
        self.assertRaises(Exception, lambda:  view.uploadFile(myUpload))

        myUpload = makeFileUpload(file, 'test.gif')
        myUpload.method = 'POST'
        myUpload.form = {}
        headers, output, request = makeResponse(myUpload)
        view = VNCCollabUtilView(self.portal, request)
        result = view.uploadFile(file)
        self.assertEqual(result, 'http://nohost/plone/foo.pdf/edit')

        myUpload = makeFileUpload(file, 'test.gif')
        myUpload.method = 'POST'
        myUpload.form = {'ajax_call': True}
        headers, output, request = makeResponse(myUpload)
        view = VNCCollabUtilView(self.portal, request)
        result = view.uploadFile(file)
        self.assertEqual(result, 'http://nohost/plone/foo.pdf-1/edit')
