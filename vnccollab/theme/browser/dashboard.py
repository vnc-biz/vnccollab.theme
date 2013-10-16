from zope.component import getUtility

from Products.Five.browser import BrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY
from plone.app.portlets.browser.manage import \
    ManageGroupDashboardPortlets as OriginalMGDPortlets

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName


class DashboardView(BrowserView):
    """User's Dashboard.

    Lists user's group assigned portlets.
    """

    @memoize
    def empty(self):
        dashboards = [getUtility(IPortletManager, name=name)
                      for name in ['plone.dashboard1',
                                   'plone.dashboard2',
                                   'plone.dashboard3',
                                   'plone.dashboard4']]

        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        userid = member.getId()

        num_portlets = 0
        for dashboard in dashboards:
            num_portlets += len(dashboard.get(USER_CATEGORY, {})
                                         .get(userid, {}))
            for groupid in member.getGroups():
                num_portlets += len(dashboard.get(GROUP_CATEGORY, {})
                                             .get(groupid, {}))
        return num_portlets == 0


class ManageGroupDashboardPortlets(OriginalMGDPortlets):
    """Manage Group Dashboard Portlets, customized for Anonymous Homepage."""
    def getAssignmentsForManager(self, manager):
        mapping = OriginalMGDPortlets.getAssignmentsForManager(self, manager)
        if not mapping:
            mapping = self.displaceMapping(manager)
        return mapping

    def displaceMapping(self, manager):
        """Moves the assigned portlets from the next non empty portlet manager
        to this one."""
        next_manager = self._nextManager(manager)
        if not next_manager:
            # There's no next manager with portlets assigned
            return []

        mapping = OriginalMGDPortlets.getAssignmentsForManager(self,
                next_manager)
        # TODO: Assign to manager
        # TODO: Delete from next_manager
        # TODO: return mapping
        return []

    def _nextManager(self, manager):
        """Returns the next non empty portlet manager."""
        # TODO:
        return None
