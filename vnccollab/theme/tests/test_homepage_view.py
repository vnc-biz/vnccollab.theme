import ast
import urllib
import transaction

from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser

from plone import api
from plone.testing.z2 import Browser
from plone.portlets.interfaces import IPortletType
from plone.app.portlets.portlets import calendar

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.retriever import PortletRetriever

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.homepage import HomePageView
from vnccollab.theme.portlets.retriever import CloudPortalDashboardPortletRetriever


# class DummyPortletRetriever(object): #PortletRetriever):
#      # implements(IPortletRetriever)
#      # adapts(Interface, IDummyPortletManager)

from zope.interface import implements
from plone.portlets.interfaces import IPortletRenderer
class DummyPortletRenderer:
    implements(IPortletRenderer)

    @property
    def available(self):
        return getattr(self, '__portlet_metadata__', False)

    def render(self):
        return u'dummy portlet renderer'

    def update(self):
        pass


class Obj(object):
    pass


def getPortlets(self):
    p = dict()
    p['category'] = CONTEXT_CATEGORY
    p['key'] = p['name'] = u'dummy'
    p['assignment'] = obj = Obj()
    obj.data = DummyPortletRenderer()
    obj.available = True
    return (p, )


class TestHomepageView(FunctionalTestCase):
    members = (
        ('secret', 'Scott Tiger', 'scott@tiger.com', ['members', 'Manager'], '2013-09-24'),
        ('secret', 'Johann Sebastian Bach', 'johan@bach.com', ['members', 'Manager'], '2013-09-24'),)

    def test_homepage(self):
        browser = self.login()
        browser.open(self.portal_url + '/@@homepage_view')

        self.assertIn('wizardContentArea', browser.contents)
        self.assertIn('wizard-steps', browser.contents)
        self.assertIn('step step1', browser.contents)
        self.assertIn('step step2', browser.contents)
        self.assertIn('ENTER CONTENT INFORMATION', browser.contents)
        self.assertIn('step step3', browser.contents)
        self.assertIn('WHERE DO YOU WANT TO PUT THE NEW ITEM?', browser.contents)
        self.assertIn('wizard-overlay', browser.contents)
        self.assertIn('Loading...', browser.contents)
        self.assertIn('<img width="80" height="80" src="http://nohost/plone/defaultUser.png" alt="test_user_1_" />', browser.contents)
        self.assertIn('<a href="http://nohost/plone/author/test_user_1_">My Profile</a>', browser.contents)
        self.assertIn('<a class="logoutLink" title="Click to logout" href="http://nohost/plone/logout">Log out</a>', browser.contents)
        self.assertIn('portal-breadcrumbs', browser.contents)
        self.assertIn('breadcrumbs-home', browser.contents)

    def test_getNews(self):
        view = HomePageView(self.portal, self.app.REQUEST)
        view()
        news = view.getNews()
        self.assertTrue(len(news) == 0)

        obj = createObject(self.portal, 'News Item', 'test_doc',
                           title='A title',
                           description='Some description',
                           text='Some text')

        news = view.getNews()
        self.assertTrue(len(news) == 1)
        self.assertEqual(news[0].getObject().title, 'A title')

    def test_render(self):
        browser = Browser(self.portal)
        browser.open(self.portal_url + '/@@homepage_view')

        self.assertIn('<title>Site</title>', browser.contents)
        self.assertIn('anonymousMode', browser.contents)
        self.assertIn('<a accesskey="2" href="http://nohost/plone/@@homepage_view#content">Skip to content.</a>', browser.contents)
        self.assertIn('<a accesskey="6" href="http://nohost/plone/@@homepage_view#portal-globalnav">Skip to navigation</a>', browser.contents)
        self.assertIn('<li><a href="http://nohost/plone/register">Sign Up</a></li>', browser.contents)
        self.assertIn('<li><a href="http://nohost/plone/login_form">Login</a></li>', browser.contents)
        self.assertIn('anonymousMode', browser.contents)

    def test_getColumn(self):
        browser = self.login('scott@tiger.com', 'secret')
        browser.open(self.portal_url + '/@@manage-group-dashboard?key=AnonymousUsers')

        form = browser.getForm(index=1)
        form.getControl(name=':action').value = [u'/++groupdashboard++plone.dashboard1+AnonymousUsers/+/vnccollab.theme.portlets.WorldClockPortlet']
        form.submit()
        form = browser.getForm(index=1)
        form.getControl(name='form.actions.save').click()

        self.logout(browser)
        browser = Browser(self.portal)
        browser.open(self.portal_url + '/@@homepage_view')

    def test_customAnonHomepage_empty(self):
        """Test Custom Anonymous homepage when it wasn't customized"""
        browser = Browser(self.portal)
        browser.open(self.portal_url)
        self.assertNotIn('<div id="custom-anon-homepage"', browser.contents)

    def test_customAnonHomepage_customized(self):
        """Test Custom Anonymous homepage when it was customized"""
        # TODO: Create custom anon page
        #self._create_custom_anon_homepage()
        browser = Browser(self.portal)
        browser.open(self.portal_url)
        #self.assertIn('id="custom-anon-homepage"', browser.contents)

    def test_customAnonHomepage_nonAnon(self):
        """Test Custom Anonymous homepage when logged in"""
        browser = self.login()
        browser.open(self.portal_url)
        self.assertNotIn('<div id="custom-anon-homepage"', browser.contents)
