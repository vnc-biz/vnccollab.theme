from zope.interface import implements
from zope.component import getMultiAdapter

from plone.app.portlets.portlets import navigation
from plone.memoize.instance import memoize
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.navtree import buildFolderTree

from Products.ATContentTypes.interfaces import IATFolder
from Acquisition import aq_inner


allowed_types = ('Folder', 'Large Folder', 'Large Plone Folder', 'Collection', 'Topic')


def _filter(data):
    to_remove = []
    for k, d in enumerate(data['children']):
        if d['portal_type'] not in allowed_types:
            to_remove.append(k)
        else:
            d['children'] = _filter(d)['children']

    for i in reversed(to_remove):
        del data['children'][i]

    return data


class NavtreeStrategyBase(navigation.NavtreeStrategy):
    """Basic navigation tree strategy that does nothing.
    """
    implements(INavtreeStrategy)

    def nodeFilter(self, node):
        result = False
        item = node['item']
        for t in allowed_types:
            if item.getObject().portal_type in allowed_types:
                result = True
                break
        return result


class Renderer(navigation.Renderer):
    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)
        queryBuilder = getMultiAdapter((context, self.data), INavigationQueryBuilder)
        strategy = NavtreeStrategyBase(context, self.data)
        result = buildFolderTree(context, obj=context, query=queryBuilder(), strategy=strategy)
        return _filter(result)