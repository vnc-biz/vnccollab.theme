from plone.indexer.decorator import indexer
from zope.annotation.interfaces import IAnnotations

from cioppino.twothumbs.interfaces import ILoveThumbsDontYou
from cioppino.twothumbs.rate import yays, nays, getTotalPositiveRatings, \
    getTally


@indexer(ILoveThumbsDontYou)
def avg_ratings(object, **kw):
    """Average rating: difference between thumb ups and downs.
    """
    total = getTally(object)
    return total['ups'] - total['downs']

@indexer(ILoveThumbsDontYou)
def total_down_ratings(object, **kw):
    """
    Return the total number of negative ratings
    """
    annotations = IAnnotations(object)
    if nays in annotations:
        return len(annotations[nays])

    return 0
