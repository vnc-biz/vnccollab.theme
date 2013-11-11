import ast
import urllib
import simplejson
import transaction

from zope.component import getUtility
from Products.CMFPlone.Portal import PloneSite
from Products.ATContentTypes.content.folder import ATFolder

from plone.portlets.interfaces import IPortletType

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.wizardjson import GetTreeJson

class WizardJsonView(FunctionalTestCase):
    def setUp(self):
        super(WizardJsonView, self).setUp()

        self.getTreeJson = GetTreeJson(self.portal, self.app.REQUEST)

    def __test_tree(self, data, json=True):
        if json:
            data = simplejson.loads(data)

        keys = ('activate', 'isFolder', 'key', 'path', 'id', 'icon', 'title',
                'url', 'unselectable', 'noLink', 'tooltip', 'children',
                'isLazy')

        for key in keys:
            self.assertIn(key, data)

        if data['children']:
            for child in data['children']:
                self.__test_tree(child, False)

    def test_getInitialTree(self):
        data = self.getTreeJson.getInitialTree()

        self.__test_tree(data)

        obj = createObject(self.portal, 'Folder', 'test_folder_1', 
                           title='A test folder',
                           description='Some description',
                           text='Some text')

        getTreeJson = GetTreeJson(obj, self.app.REQUEST)
        data = getTreeJson.getInitialTree()
        self.__test_tree(data)

    def test_getRootNode(self):
        tree = self.getTreeJson.getRootNode()
        self.__test_tree(tree, False)

    def test_getFolderishParent(self):
        data1 = self.getTreeJson.getFolderishParent(self.portal)
        self.assertTrue(isinstance(data1, PloneSite))

        obj = createObject(self.portal, 'Folder', 'test_folder_1', 
                           title='A test folder',
                           description='Some description',
                           text='Some text')

        data2 = self.getTreeJson.getFolderishParent(obj)
        self.assertTrue(isinstance(data2, ATFolder))

    def test_getTree(self):
        tree = self.getTreeJson.getTree()
        tree = simplejson.loads(tree)
        self.__test_tree(tree[0], False)

    def test_get_tree(self):
        tree = self.getTreeJson.get_tree()[0]
        self.assertEqual(tree['path'], '/plone/events')
        self.assertEqual(tree['id'], 'events')
        self.assertEqual(tree['url'], 'http://nohost/plone/events')
        self.__test_tree(tree, False)

        obj = createObject(self.portal, 'Folder', 'test_folder_1', 
                           title='A test folder',
                           description='Some description',
                           text='Some text')

        tree = self.getTreeJson.get_tree(uid='test_folder_1')[0]
        self.assertEqual(tree['path'], '/plone/test_folder_1')
        self.assertEqual(tree['id'], 'test_folder_1')
        self.assertEqual(tree['url'], 'http://nohost/plone/test_folder_1')
        self.__test_tree(tree, False)
