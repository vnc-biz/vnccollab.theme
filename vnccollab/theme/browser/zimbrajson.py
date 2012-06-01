import json
import base64

from zope.interface import Interface, implements
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from wsapi4plone.core.browser.app import ApplicationAPI

'''
This module contains the views to allow Zimbra to interact with plone.

All these views are server as XMLRPC methods. They return a string with the
result encoded as JSON.
'''

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

    Returns a string with a JSON representation of the current object.

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


class GetTreeJson(BrowserView):
    '''Returns a string with a JSON representation of the tree of folders
    accesible by the current user.
    '''
    CONTAINER_TYPES = ['Folder']

    def __call__(self, REQUEST, RESPONSE):
        result = self._get_tree()
        RESPONSE.setHeader('Content-Type', 'application/json')
        #return result
        return json.dumps(result)

    def _get_tree(self):
        # TODO: Search only below context
        catalog = self.context.portal_catalog
        params = {'portal_type': self.CONTAINER_TYPES,}
        results = [self._dict_from_brain(x) for x in catalog(**params)]
        results = self._sorted(results, reverse=True)
        tree = self._create_tree(results)
        tree = self._sort_tree(tree)
        return tree

    def _dict_from_brain(self, brain):
        '''Returns a dict representing the folder, given a brain'''
        return {'id': brain.getId,
                'title' : brain.Title,
                'path' : brain.getPath(),
                'portal_type': brain.portal_type,
                'content' : []}

    def _sorted(self, lst, reverse=False):
        '''Returns the folders sorted by the lenght of its path'''
        return sorted(lst, lambda x, y: cmp(len(x['path']), len(y['path'])),
                      reverse=reverse)

    def _inside(self, son, father):
        '''True if the folder son is inside father'''
        return son['path'].startswith(father['path'])

    def _create_tree(self, lst):
        tree = []
        for i, e in enumerate(lst):
            for f in lst[i+1:]:
                if self._inside(e, f):
                    f['content'].append(e)
                    break
            else:
                tree.append(e)
        return tree

    def _sort_tree(self, tree):
        tree = sorted(tree, lambda x, y: cmp(x['title'], y['title']))
        for e in tree:
            e['content'] = self._sort_tree(e['content'])
        return tree


