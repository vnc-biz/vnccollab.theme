from Acquisition import aq_inner
from ZODB.POSException import ConflictError

from zope.component import getUtility
from zope.interface import Interface, implements, alsoProvides

from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager, \
   IPortletAssignmentSettings
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.manager import PortletManagerRenderer, logger
from plone.portlets.utils import hashPortletInfo

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from ..config import HP_NEWS_LIMIT
from .dashboard import DashboardView


class IHomePageView(Interface):
    """Homepage Default View"""

class IAnonymousHomePageView(IHomePageView):
    """Marker interface for anonymous homepage version"""

class HomePageColumnsRenderer(PortletManagerRenderer):

    @memoize
    def _lazyLoadPortlets(self, manager):
        items = []
        # below assignments attribute should be assigned by parent code
        for p in self.filter(self.assignments):
            renderer = self._dataToPortlet(p['assignment'].data)
            info = p.copy()
            info['manager'] = self.manager.__name__
            info['renderer'] = renderer
            hashPortletInfo(info)
            # Record metadata on the renderer
            renderer.__portlet_metadata__ = info.copy()
            del renderer.__portlet_metadata__['renderer']
            try:
                isAvailable = renderer.available
            except ConflictError:
                raise
            except Exception, e:
                isAvailable = False
                logger.exception(
                    "Error while determining renderer availability of portlet "
                    "(%r %r %r): %s" % (
                    p['category'], p['key'], p['name'], str(e)))

            info['available'] = isAvailable
            items.append(info)

        return items

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
        if self.is_anonymous():
            alsoProvides(self, IAnonymousHomePageView)
        return self.render()

    def render(self):
        if self.is_anonymous():
            return self._welcome_template()
        else:
            return self._dashboard_template()

    def getColumn(self, name, group='AnonymousUsers'):
        column = getUtility(IPortletManager, name=name)
        category = column[GROUP_CATEGORY]
        mapping = category.get(group, None)
        if mapping is None:
            return u''

        context = aq_inner(self.context)
        assignments = []
        for assignment in mapping.values():
            settings = IPortletAssignmentSettings(assignment)
            if not settings.get('visible', True):
                continue
            assignments.append({'category': GROUP_CATEGORY,
                                'key': group,
                                'name': assignment.__name__,
                                'assignment': assignment
                                })

        renderer = HomePageColumnsRenderer(context, self.request, self, column)
        renderer.assignments = assignments
        renderer.update()
        return renderer.render()

    def is_anonymous(self):
        mt = getToolByName(self.context, 'portal_membership')
        return mt.isAnonymousUser()
