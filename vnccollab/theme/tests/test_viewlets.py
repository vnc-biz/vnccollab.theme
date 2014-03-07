from DateTime import DateTime

from zope.publisher.browser import TestRequest
from zope.i18nmessageid import MessageFactory

from Products.CMFPlone.i18nl10n import monthname_msgid, weekdayname_msgid
from Products.CMFPlone.utils import safe_unicode

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.viewlets import TopRatedViewlet, \
    ActionsListViewlet, LoginViewlet, HeaderTimeViewlet, \
    VNCCollabHeaderViewlet, WorldClockViewlet, ZopeEditViewlet


_pl = MessageFactory('plonelocales')


class DummyActionsTool:
    def __init__(self, actions=None):
        if actions is None:
            actions = {}
        self.actions = actions.copy()

    def listFilteredActionsFor(self, context):
        return self.actions

    def listActionInfos(self, action_chain=None, object=None, check_visibility=True,
                        check_permissions=True, check_condition=True, max=None):
        if action_chain is not None:
            return [{'url': '%s/test_url' % action_chain}]
        return []


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
        request = self.app.REQUEST
        viewlet = LoginViewlet(self.portal, request, None, None)
        self.assertEqual(viewlet.join_action(), None)

        request = self.app.REQUEST
        viewlet = LoginViewlet(self.portal, request, None, None)
        viewlet.context.portal_actions = DummyActionsTool()
        self.assertEqual(viewlet.join_action(), 'user/join/test_url')

        self.assertEqual(viewlet.can_register(), 1)
        viewlet.context.portal_registration = None
        self.assertFalse(viewlet.can_register())

        self.assertTrue(viewlet.can_request_password())

        viewlet.membership.checkPermission = lambda s, c: False
        self.assertFalse(viewlet.can_request_password())

    def test_HeaderTimeViewlet(self):
        request = self.app.REQUEST
        viewlet = HeaderTimeViewlet(self.portal, request, None, None)
        viewlet.update()

        date = DateTime()
        self.assertEqual(viewlet.day, date.day())

        month = _pl(monthname_msgid(int(date.strftime('%m'))),
            default=safe_unicode(date.Month()))
        dayname = _pl(weekdayname_msgid(int(date.strftime('%w'))),
            default=safe_unicode(date.DayOfWeek()))
        datetime = viewlet.toLocalizedTime(date, long_format=True)
        self.assertEqual(viewlet.month, month)
        self.assertEqual(viewlet.dayname, dayname)
        self.assertEqual(viewlet.datetime, datetime)

    def test_WorldClockViewlet(self):
        request = self.app.REQUEST
        viewlet = WorldClockViewlet(self.portal, request, 
            self.portal.restrictedTraverse('@@plone'), None)
        viewlet.update()

        self.assertIn('class="worldClockWrapper"', viewlet.world_clock)
        self.assertIn('id="c1"', viewlet.world_clock)
        self.assertIn('id="c2"', viewlet.world_clock)
        self.assertIn('id="c3"', viewlet.world_clock)
        self.assertIn('class="worldClockCity"', viewlet.world_clock)
        self.assertIn(
            'src="http://nohost/plone/++resource++vnccollab.theme.js/coolclock.js"',
            viewlet.world_clock)
        self.assertIn('CoolClock.config', viewlet.world_clock)

    def test_ZopeEditViewlet(self):
        request = self.app.REQUEST
        viewlet = ZopeEditViewlet(self.portal, request, 
            self.portal.restrictedTraverse('@@plone'), None)
        viewlet.update()
        self.assertEqual(viewlet.external_editor_url(), 
            '/externalEdit_/plone.zem')

