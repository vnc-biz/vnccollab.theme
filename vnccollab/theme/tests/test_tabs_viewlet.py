from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.interfaces import IViewlet

from Products.Five.browser import BrowserView as View

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject, CAST_ENABLED


class TabsViewletView(FunctionalTestCase):
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

    def test_cast_tab(self):
        if not CAST_ENABLED:
            return

        browser = self.login()
        obj = createObject(self.portal, 'CastsContainer', 'test_castcontainer', 
                   title='Some cast container',
                   description='Some cast container description',
                   text='Some text')

        # content tab selected
        browser.open(self.portal_url)
        self.assertIn('<ul id="portal-globalnav"><li id="portaltab-content" class="selected"><a href="http://nohost/plone" title="content">Content</a></li><li id="portaltab-cast" class="plain"><a href="http://nohost/plone/test_castcontainer" title="cast">Cast</a></li></ul>', browser.contents)

        # cast tab selected
        browser.open(obj.absolute_url())
        self.assertIn('<ul id="portal-globalnav"><li id="portaltab-content" class="plain"><a href="http://nohost/plone" title="content">Content</a></li><li id="portaltab-cast" class="selected"><a href="http://nohost/plone/test_castcontainer" title="cast">Cast</a></li></ul>', browser.contents)
