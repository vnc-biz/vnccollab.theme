from zope.interface import Interface, implements

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from vnccollab.theme.config import HP_NEWS_LIMIT


class IHomePageView(Interface):
    """Homepage Default View"""

class HomePageView(BrowserView):

    implements(IHomePageView)

    homepage = ViewPageTemplateFile('templates/homepage_view.pt')
    dashboard = ViewPageTemplateFile('templates/dashboard.pt')

    def getNews(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type="News Item", sort_on='created',
            sort_order='reverse',
            sort_limit=HP_NEWS_LIMIT)[:HP_NEWS_LIMIT]

    def __call__(self):
        return self.render()

    def render(self):
        if self.is_anonymous():
            return self.homepage()
        else:
            dashboard_url = self.context.absolute_url() + '/dashboard'
            return self.request.response.redirect(dashboard_url)

    def is_anonymous(self):
        mt = getToolByName(self.context, 'portal_membership')
        return mt.isAnonymousUser()
