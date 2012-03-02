from AccessControl import getSecurityManager

from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.annotation.interfaces import IAnnotations

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.app.portlets.interfaces import IColumn, IDashboard
from plone.memoize.instance import memoize

from plone.portlets.interfaces import IPortletManager
from plone.app.portlets import manager
from plone.app.portlets.browser import editmanager
from plone.app.portlets.browser.interfaces import IManageColumnPortletsView, \
    IManageContextualPortletsView, IManageDashboardPortletsView

from vnccollab.theme.browser.interfaces import IThemeSpecific
from vnccollab.theme.config import PORTLETS_STATES_ANNO_KEY


class ColumnPortletManagerRenderer(manager.ColumnPortletManagerRenderer):
    """A renderer for the column portlets
    """
    adapts(Interface, IThemeSpecific, IBrowserView, IColumn)
    template = ViewPageTemplateFile('templates/portlets-column.pt')

    def portlet_states(self, hash):
        return self._portlets_states().get(hash, {})

    @memoize
    def _portlets_states(self):
        """Returns portlets states settings for currently logged in user."""
        user = getSecurityManager().getUser()
        if not user or getattr(user, 'name', '') == 'Anonymous User':
            return {}
        
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        annotations = IAnnotations(portal)
        users = annotations.get(PORTLETS_STATES_ANNO_KEY, None)
        if users is None:
            return {}
        
        userid = getattr(user, '_id', user.getId())
        return users.get(userid, {})

class DashboardPortletManagerRenderer(ColumnPortletManagerRenderer):
    """Render a column of the dashboard
    """
    adapts(Interface, IThemeSpecific, IBrowserView, IDashboard)
    template = ViewPageTemplateFile('templates/portlets-dashboard-column.pt')

class EditPortletManagerRenderer(editmanager.EditPortletManagerRenderer):
    adapts(Interface, IThemeSpecific, IManageColumnPortletsView,
        IPortletManager)

class ContextualEditPortletManagerRenderer(
    editmanager.ContextualEditPortletManagerRenderer):
    adapts(Interface, IThemeSpecific, IManageContextualPortletsView,
        IPortletManager)

class DashboardEditPortletManagerRenderer(
    editmanager.DashboardEditPortletManagerRenderer):
    adapts(Interface, IThemeSpecific, IManageDashboardPortletsView,
        IDashboard)
