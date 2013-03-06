from zope.interface import Interface, implements

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from ..config import HP_NEWS_LIMIT
from .dashboard import DashboardView


class IHomePageView(Interface):
    """Homepage Default View"""

class HomePageView(DashboardView):

    implements(IHomePageView)

    _welcome_template = ViewPageTemplateFile('templates/homepage_view.pt')
    _dashboard_template = ViewPageTemplateFile('templates/dashboard.pt')

    def getNews(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type="News Item", sort_on='created',
            sort_order='reverse',
            sort_limit=HP_NEWS_LIMIT)[:HP_NEWS_LIMIT]

    def __call__(self):
        return self.render()

    def render(self):
        if self.is_anonymous():
            return self._welcome_template()
        else:
            return self._dashboard_template()

    def is_anonymous(self):
        mt = getToolByName(self.context, 'portal_membership')
        return mt.isAnonymousUser()
