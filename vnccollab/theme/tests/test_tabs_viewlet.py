from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.interfaces import IViewlet

from Products.Five.browser import BrowserView as View
from plone.app.viewletmanager.manager import BaseOrderedViewletManager

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.browser.viewlets import TabsViewlet
from vnccollab.theme.testing import createObject


class TabsViewletView(FunctionalTestCase):
    members = (
        ('secret', 'Scott Tiger', 'scott@tiger.com', ['members'], '2013-09-24'),
        ('secret', 'Johann Sebastian Bach', 'johan@bach.com', ['members'], '2013-09-24'),)

    def test_viewlet_is_present(self):
        view = View(self.portal, self.request)

        manager = queryMultiAdapter((self.portal, self.request, view), IViewletManager, 'plone.portalheader', default=None)
        manager.update()

        my_viewlet = [v for v in manager.viewlets if v.__name__ == 'vnccollab.theme.toptabs']
        self.assertEqual(len(my_viewlet), 1)

        viewlet = queryMultiAdapter((self.portal, self.request, view,
            manager), IViewlet, name='vnccollab.theme.toptabs')

    def test_no_cast_tab(self):
        browser = self.login()

        browser.open(self.portal_url)
        self.assertIn('<ul id="portal-globalnav"><li id="portaltab-content" class="selected"><a href="http://nohost/plone" title="content">Content</a></li></ul>', browser.contents)

    #def test_cast_tab(self):
    #    browser = self.login()
    #    createObject
