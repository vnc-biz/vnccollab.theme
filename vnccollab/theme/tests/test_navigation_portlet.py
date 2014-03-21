import json
import urllib
import transaction

from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.portlets import navigation

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.portlets.navigation import Renderer


class NavigationRendererTest(FunctionalTestCase):
    def setUp(self):
        super(NavigationRendererTest, self).setUp()
        self.populateSite()

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.app.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or navigation.Assignment(topLevel=0)

        return Renderer(context, request, view, manager, assignment)

    def populateSite(self):
        self.setRoles(['Manager'])
        if 'Members' in self.portal:
            self.portal._delObject('Members')
            self.folder = None
        if 'news' in self.portal:
            self.portal._delObject('news')
        if 'events' in self.portal:
            self.portal._delObject('events')
        if 'front-page' in self.portal:
            self.portal._delObject('front-page')
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        self.portal.invokeFactory('Link', 'link1')
        self.portal.link1.setRemoteUrl('http://plone.org')
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('Document', 'doc12')
        folder1.invokeFactory('Document', 'doc13')
        self.portal.invokeFactory('Folder', 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        folder2.invokeFactory('Document', 'doc21')
        folder2.invokeFactory('Document', 'doc22')
        folder2.invokeFactory('Document', 'doc23')
        folder2.invokeFactory('File', 'file21')
        folder2.invokeFactory('Folder', 'folder21')
        self.setRoles(['Member'])

    def _test_tree(self, tree, allowed, selected=False):
        for el in tree:
            self.assertIn(el['id'], allowed)
            if selected and el['normalized_id'] == selected:
                self.assertTrue(el['currentItem'])
            if el['children']:
                self._test_tree(el['children'], allowed)

    def test_CreateNavTree(self):
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        self.failUnless(tree)
        self.failUnless(tree['children'], tree)
        self._test_tree(tree['children'], ('folder1', 'folder2'))

    def test_CreateNavTreeCurrentItem(self):
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        self._test_tree(tree['children'], ('folder1', 'folder2', 'folder21'))

    def test_checkSelections(self):
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        self._test_tree(tree['children'], ('folder1', 'folder2', 'folder21'), 'folder2')

        view = self.renderer(self.portal.folder2.doc22)
        tree = view.getNavTree()
        self._test_tree(tree['children'], ('folder1', 'folder2', 'folder21'), 'folder2')

        view = self.renderer(self.portal.folder1.doc11)
        tree = view.getNavTree()
        self._test_tree(tree['children'], ('folder1', 'folder2', 'folder21'), 'folder1')
