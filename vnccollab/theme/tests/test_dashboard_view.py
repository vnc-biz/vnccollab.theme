import ast
import urllib
import transaction

from zope.component import getUtility

from plone.portlets.interfaces import IPortletType

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject


class TestDashboardView(FunctionalTestCase):
    def test_homepage(self):
        browser = self.login()
        browser.open(self.portal_url + '/@@dashboard')

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

    def test_manage_dashboard(self):
        browser = self.login()

        browser.open(self.portal_url + '/@@manage-dashboard')
        self.assertIn('Edit your dashboard', browser.contents)
        portlets = [
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.Calendar">Calendar portlet</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.Classic">Classic portlet</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.Events">Events</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.News">News</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.PubSubFeed">PubSub feed portlet</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.rss">RSS Feed</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.Recent">Recent items</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.Review">Review list</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.Search">Search</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/sc.social.bookmarks.sb_portlet">Social Bookmarks Portlet</option>',
            '<option value="/++dashboard++plone.dashboard1+test_user_1_/+/portlets.Subscription">Subscription portlet</option>']
        self.assertIn('Edit your dashboard', browser.contents)
        self.assertNotIn('managedPortlet', browser.contents)
        self.assertNotIn('managedPortletActions', browser.contents)
        self.assertNotIn('Search</a>', browser.contents)

        form = browser.getForm(index=1)
        form.getControl(name=':action').value = [u'/++dashboard++plone.dashboard1+test_user_1_/+/portlets.Search']
        form.submit()
        form = browser.getForm(id='zc.page.browser_form')
        form.getControl(name='form.actions.save').click()

        browser.open(self.portal_url + '/@@manage-dashboard')
        self.assertIn('Portlets assigned here', browser.contents)
        self.assertIn('managedPortlet', browser.contents)
        self.assertIn('managedPortletActions', browser.contents)
        self.assertIn('Search</a>', browser.contents)
