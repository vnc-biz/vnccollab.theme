from zope.interface import Interface, implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

import json


class LiveSearchReplyJson(BrowserView):
    OMIT_TYPES = ['Folder']

    def search(self, query):
        '''Returns the objects in the catalog that satisfy the query'''
        catalog = self.context.portal_catalog
        plone_utils = getToolByName(self.context, 'plone_utils')
        friendly_types = plone_utils.getUserFriendlyTypes()
        r = ' AND '.join(query.split())
        params = {'SearchableText': r,
                  'portal_type': friendly_types,}
        results = catalog(**params)
        return results

    def _tuples_from_brains(self, brains):
        '''Converts a list of brains to a list of tuples'''
        plone_view = self.context.restrictedTraverse('@@plone')
        ploneUtils = getToolByName(self.context, 'plone_utils')
        pretty_title_or_id = ploneUtils.pretty_title_or_id

        tuples = []

        for brain in brains:
            icon = plone_view.getIcon(brain).url
            type_ = brain.portal_type
            title = pretty_title_or_id(brain)
            url = brain.getURL()

            if type_ not in self.OMIT_TYPES:
                tuples.append((icon, type_, title, url))

        return tuples

    def _get_query_string(self, query):
        '''Cleans the query string sanitized'''
        multispace = u'\u3000'.encode('utf-8')
        for char in ('?', '-', '+', '*', multispace):
                query = query.replace(char, ' ')
        return query

    def __call__(self, REQUEST, RESPONSE):
        '''Returns a JSON representation of the objects that satisfy the query'''
        brains = self.search(self._get_query_string(REQUEST))
        results = self._tuples_from_brains(brains)
        RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps(results)

