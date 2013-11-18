from zope.publisher.browser import TestRequest

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.viewlets import TopRatedViewlet, \
    ActionsListViewlet, LoginViewlet


class TestViewlets(FunctionalTestCase):
    def test_TopRatedViewlet(self):
        request = self.app.REQUEST
        viewlet = TopRatedViewlet(self.portal, request, None, None)
        viewlet.update()

        for elem in viewlet.elems:
            self.assertIn('url', elem)
            self.assertIn('rating', elem)
            self.assertIn('desc', elem)
            self.assertIn('type', elem)
            self.assertIn('title', elem)

            self.assertIn('liked', elem['rating'])
            self.assertIn('total', elem['rating'])
            self.assertIn('disliked', elem['rating'])

    def test_ActionsListViewlet(self):
        request = self.app.REQUEST
        viewlet = ActionsListViewlet(self.portal, request, None, None)
        viewlet.update()
        self.assertTrue(viewlet.todo is None)

    def test_LoginViewlet(self):
        return
        from Products.CMFCore.ActionsTool import ActionsTool

        self.site._setObject('portal_actions', ActionsTool('portal_actions'))

        request = self.app.REQUEST
        viewlet = LoginViewlet(self.portal, request, None, None)
        viewlet.update()
        print viewlet.join_action()