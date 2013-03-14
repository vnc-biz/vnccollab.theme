from plone import api
from Products.Five.browser import BrowserView

from wsapi4plone.core.browser.app import ApplicationAPI


class WSAPIView(BrowserView):

    def post_and_index_object(self, params):
        wsapi = ApplicationAPI(self.context, self.request)
        results = wsapi.post_object(params)
        self._reindex_paths(results)
        return results

    def _reindex_paths(self, paths):
        portal = api.portal.get()
        for path in paths:
            object = portal.unrestrictedTraverse(path)
            object.reindexObject()
