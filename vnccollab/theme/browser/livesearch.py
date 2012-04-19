import json
import base64

from zope.interface import Interface, implements
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from wsapi4plone.core.browser.app import ApplicationAPI


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

    def _get_lost_icon(self, brain):
        '''Gets the icon of a brain if it is not present'''
        return '{0}{1}'.format(self.context.portal_url(),
                               '/++resource++vnccollab.theme.images/doc.png')

    def _tuples_from_brains(self, brains):
        '''Converts a list of brains to a list of tuples'''
        plone_view = self.context.restrictedTraverse('@@plone')
        ploneUtils = getToolByName(self.context, 'plone_utils')
        pretty_title_or_id = ploneUtils.pretty_title_or_id

        tuples = []

        for brain in brains:
            icon = plone_view.getIcon(brain).url or self._get_lost_icon(brain)
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



class GetObjectJson(BrowserView):
    '''Implements get_object_json.

    Returns a JSON representation of the current object.

    The representation is a dictionary with the data obtained by wsapi4plone's
    get_object with dates converted to strings.'''

    def __call__(self, REQUEST, RESPONSE):
        '''Returns a JSON representation of the current object'''
        wsapi = ApplicationAPI(self.context, self.request)
        my_path =self.context.absolute_url_path()
        results = wsapi.get_object([my_path])
        # One result is a tuple (object_data, object_type, extra_info)
        # We're interested only in object_data
        result = results[my_path][0]
        self._sanitize_results(result)
        RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps(result)

    SANITIZE_FIELDS = ['DateTime']

    def _sanitize_results(self, result):
        #import pdb; pdb.set_trace()
        for k,v in result.items():
            if v.__class__.__name__ in self.SANITIZE_FIELDS:
                result[k] = str(v)

        # Convert file data to string instead of xmlrpclib.Binary
        if 'file' in result:
            result['file']['data'] = base64.b64encode(result['file']['data'].data)

