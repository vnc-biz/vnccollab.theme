from zope.interface import implements
from zope.component import getMultiAdapter

from plone.app.portlets.portlets import navigation
from plone.memoize.instance import memoize
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.navtree import buildFolderTree

from Products.ATContentTypes.interfaces import IATFolder
from Acquisition import aq_inner


allowed_types = (IATFolder,)


class NavtreeStrategyBase(navigation.NavtreeStrategy):
    """Basic navigation tree strategy that does nothing.
    """
    implements(INavtreeStrategy)

    def nodeFilter(self, node):
        result = False
        item = node['item']
        for t in allowed_types:
            if t.providedBy(item.getObject()):
                result = True
                break
        return result


class Renderer(navigation.Renderer):
    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)
        queryBuilder = getMultiAdapter((context, self.data), INavigationQueryBuilder)
        strategy = NavtreeStrategyBase(context, self.data)
        return buildFolderTree(context, obj=context, query=queryBuilder(), strategy=strategy)