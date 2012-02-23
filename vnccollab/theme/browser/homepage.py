from zope.interface import Interface, implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from vnccollab.theme.config import HP_NEWS_LIMIT


class IHomePageView(Interface):
    """Homepage Default View"""

class HomePageView(BrowserView):
    
    implements(IHomePageView)
    
    def getNews(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type="News Item", sort_on='created',
            sort_order='reverse',
            sort_limit=HP_NEWS_LIMIT)[:HP_NEWS_LIMIT]
