from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, normalizeString

from plone.app.layout.viewlets.common import ViewletBase

from cioppino.twothumbs.rate import getTally
from vnccollab.theme import messageFactory as _


class TopRatedViewlet(ViewletBase):
    """Renders list of most rated items under given container.
    
    Rating system by cioppino.twothumbs.
    """
    
    def update(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        elems = []
        for brain in catalog(path={'depth': 20,
            'query': '/'.join(self.context.getPhysicalPath())},
            sort_on='avg_ratings',
            sort_order='reverse'):
            
            # skip item if nobody voted yet
            if brain.positive_ratings == 0 and brain.total_down_ratings == 0:
                continue
            
            elems.append({
                'title': _(safe_unicode(brain.Title)),
                'desc': _(safe_unicode(brain.Description)),
                'url': brain.getURL(),
                'type': normalizeString(brain.portal_type, encoding='utf-8'),
                'rating': {'total': brain.avg_ratings,
                           'liked': brain.positive_ratings,
                           'disliked': brain.total_down_ratings}})
        
        self.elems = tuple(elems)
