import ast
import urllib
import simplejson
import transaction
from lxml import html

from zope.component import getUtility
from zope.publisher.browser import TestRequest
from Products.CMFPlone.Portal import PloneSite
from Products.ATContentTypes.content.folder import ATFolder

from plone.portlets.interfaces import IPortletType

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.livesearch import LiveSearchReplyView

class TestLiveSearchReplyViewView(FunctionalTestCase):
    def setUp(self):
        super(TestLiveSearchReplyViewView, self).setUp()

        # prepare some testing data
        folder_1 = createObject(
            self.portal, 'Folder', 'test_folder_1', title='Folder 1',
            description='Some Folder 1 description - itsfolder',
            text='Some Folder 1 text')
        self.folder_1 = folder_1

        document_1_folder_1 = createObject(
            folder_1, 'Document', 'test_doc_1_folder_1', title='A title doc 1 - testing very long title - longtitle',
            description='Some description of document 1 - itsdocument',
            text='Some text of document 1 from folder 1')

        document_2_folder_1 = createObject(
            folder_1, 'Document', 'test_doc_2_folder_1', title='A title doc 2',
            description='Some description of document 2 - itsdocument',
            text='Some text of document 2 from folder 1')

        folder_1_1 = createObject(
            folder_1, 'Folder', 'test_folder_1_1', title='Folder 1.1',
            description='Some Folder 1.1 description - itsfolder',
            text='Some Folder 1.1 text')

        document_1_folder_1_1 = createObject(
            folder_1, 'Document', 'test_doc_1_folder_1_1', title='A title doc 1',
            description='Some description of document 1 - itsdocument',
            text='Some text of document 1 from folder 1.1')

        folder_1_2 = createObject(
            folder_1, 'Folder', 'test_folder_1_2', title='Folder 1.2',
            description='Some Folder 1.2 description - itsfolder',
            text='Some Folder 1.2 text')

        document_1_folder_1_2 = createObject(
            folder_1_2, 'Document', 'test_doc_1_folder_1_2', title='A title doc 1',
            description='Some description of document 1 - itsdocument',
            text='Some text of document 1 from folder 1.2')

        document_2_folder_1_2 = createObject(
            folder_1_2, 'Document', 'test_doc_2_folder_1_2', title='A title doc 2',
            description='Some description of document 2 - itsdocument - string prepared especially for testing very long description test - longdescription',
            text='Some text of document 2 from folder 1.2')

        folder_2 = createObject(
            self.portal, 'Folder', 'test_folder_2', title='Folder 2',
            description='Some Folder 2 description - itsfolder',
            text='Some Folder 2 text')

        folder_2_1 = createObject(
            folder_2, 'Folder', 'test_folder_2_1', title='Folder 2.1',
            description='Some Folder 2.1 description - itsfolder',
            text='Some Folder 2.1 text')

        document_1_folder_2_1 = createObject(
            folder_2_1, 'Document', 'test_doc_1_folder_2_1', title='A title doc 1',
            description='Some description of document 1 - itsdocument',
            text='Some text of document 1 from folder 2.1')

    def _prepareView(self, request):
        return LiveSearchReplyView(self.portal, request)

    def test_no_results(self):
        request = TestRequest(form=dict(q='foo bar'))
        view = self._prepareView(request)
        self.assertIn('No matching results found.', view.result())
        self.assertIn('LSNothingFound', view.result())

    def test_search_folders(self):
        request = TestRequest(form=dict(q='itsfolder'))
        view = self._prepareView(request)
        result = view.result()

        root = html.fromstring(result) #.getroot()
        self.assertIn('Advanced Search', root.find_class('LSRow')[-1].find('a').text)
        self.assertTrue(len(root.find_class('LSRow')) == 6)
        for child in root.find_class('LSRow'):
            ctype = child.find_class('LSType')
            ctype = ctype[0] if len(ctype) > 0 else None
            if ctype is not None:
                self.assertEqual(ctype.text, 'Folder')

    def test_search_document(self):
        request = TestRequest(form=dict(q='itsdocument'))
        view = self._prepareView(request)
        result = view.result()

        root = html.fromstring(result) #.getroot()
        self.assertIn('Advanced Search', root.find_class('LSRow')[-1].find('a').text)
        self.assertTrue(len(root.find_class('LSRow')) == 7)
        for child in root.find_class('LSRow'):
            ctype = child.find_class('LSType')
            ctype = ctype[0] if len(ctype) > 0 else None
            if ctype is not None:
                self.assertEqual(ctype.text, 'Page')

    def test_search_mixed(self):
        request = TestRequest(form=dict(q='some'))
        view = self._prepareView(request)
        result = view.result()

        root = html.fromstring(result) #.getroot()
        self.assertIn('Advanced Search', root.find_class('LSRow')[-1].find('a').text)
        self.assertTrue(len(root.find_class('LSRow')) == 12)
        for child in root.find_class('LSRow'):
            ctype = child.find_class('LSType')
            ctype = ctype[0] if len(ctype) > 0 else None
            if ctype is not None:
                self.assertTrue(ctype.text in ('Page', 'Folder'))

    def test_search_path(self):
        request = TestRequest(form=dict(q='some', path=self.folder_1.absolute_url_path()))
        view = self._prepareView(request)
        result = view.result()

        root = html.fromstring(result) #.getroot()
        self.assertIn('Advanced Search', root.find_class('LSRow')[-1].find('a').text)
        self.assertTrue(len(root.find_class('LSRow')) == 9)
        for child in root.find_class('LSRow'):
            ctype = child.find_class('LSType')
            ctype = ctype[0] if len(ctype) > 0 else None
            if ctype is not None:
                self.assertTrue(ctype.text in ('Page', 'Folder'))

    def test_search_limit(self):
        request = TestRequest(form=dict(q='some', limit=5))
        view = self._prepareView(request)
        result = view.result()

        root = html.fromstring(result) #.getroot()
        self.assertIn('Advanced Search', root.find_class('LSRow')[-1].find('a').text)
        self.assertIn('Show all items', root.find_class('LSRow')[-2].find('a').text)
        self.assertTrue(len(root.find_class('LSRow')) == 7)
        for child in root.find_class('LSRow'):
            ctype = child.find_class('LSType')
            ctype = ctype[0] if len(ctype) > 0 else None
            if ctype is not None:
                self.assertTrue(ctype.text in ('Page', 'Folder'))

    def test_search_longtitle(self):
        request = TestRequest(form=dict(q='longtitle', limit=5))
        view = self._prepareView(request)
        result = view.result()
        root = html.fromstring(result)
        self.assertIn(
            'A title doc 1 - testing very ...',
            root.find_class('LSRow')[0].find_class('ls-content-title')[0].text)

    def test_search_longdescription(self):
        request = TestRequest(form=dict(q='longdescription', limit=5))
        view = self._prepareView(request)
        result = view.result()
        root = html.fromstring(result)
        self.assertIn(
            'Some description of document 2 - itsdocument - string prepared especially for testing very lo...',
            root.find_class('LSRow')[0].find_class('LSDescr')[0].text)
