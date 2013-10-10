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

    ANONYMOUS_KEY = 'AnonymousUsers'

    '''List of the names of the portlets that are allowed to be
    shown in @@manage-group-dashboard?key=AnonymousUsers.

    The name is the last part of the path in the <option> value.
    '''
    allowed_portlets = [
        'portlets.Calendar',
        'portlets.Events',
        'portlets.News',
        'collective.plonetruegallery.gallery',
        'portlets.rss',
        'portlets.Recent',
        'portlets.Search',
        'vnccollab.theme.portlets.WorldClockPortlet',
    ]

    def is_anonymous_group(self):
        '''true if we are viewing the dashboard for anonymous homepage.'''
        return self.request.get('key', '') == self.ANONYMOUS_KEY

    def addable_portlets(self):
        '''Overrides parent's portlets to show only a few, if it's for
        anonymous group.'''
        portlets = editmanager.DashboardEditPortletManagerRenderer. \
            addable_portlets(self)

        if self.is_anonymous_group():
            allowed = []
            for portlet in portlets:
                name = portlet['addview'].split('/')[-1]
                if name in self.allowed_portlets:
                    allowed.append(portlet)
            return allowed
        else:
            return portlets
