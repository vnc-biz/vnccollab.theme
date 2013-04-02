import simplejson

from Acquisition import aq_parent
from AccessControl import getSecurityManager

from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot

from plone import api
from plone.uuid.interfaces import IUUID
from plone.app.contentlisting.interfaces import IContentListing


class GetTreeJson(BrowserView):
    '''Returns a JSON representation of the directory structure
       to be used by jquery.dynatree library.'''

    def getInitialTree(self):
        '''Returns the initial tree for the dynatree.'''
        context = self.context
        child_tree = None
        child_uid = None

        while True:
            is_root = ISiteRoot.providedBy(context)

            if is_root:
                uid = None
            else:
                uid = IUUID(context)
            tree = self.get_tree(uid)

            if child_tree is not None:
                self._insert_child_tree(tree, child_tree, child_uid)

            if is_root:
                break

            context = aq_parent(context)
            child_tree = tree
            child_uid = uid

        return simplejson.dumps(tree)

    def _insert_child_tree(self, tree, child_tree, child_uid):
        for branch in tree:
            if branch.get('key', False) == child_uid:
                branch['children'] = child_tree
                branch['isLazy'] = False
                branch['expand'] = True

    def getTree(self, uid=None):
        '''Returns the (lazy) tree for a given node.

           params:
               uid: UUID of the container to get its tree.
        '''
        results = self.get_tree(uid=uid)
        return simplejson.dumps(results)

    def get_tree(self, uid=None):
        catalog = getToolByName(self.context, 'portal_catalog')

        container_path = ''
        if uid is not None:
            container = catalog(UID=uid)
            if len(container) == 1:
                container = container[0]
                container_path = container.getPath()

        if not container_path:
            portal = api.portal.get()
            container_path = portal.absolute_url_path()

        query = {'portal_type': self._get_container_types(),
                 'path': {'query': container_path, 'depth': 1}}

        results = IContentListing(catalog(**query))
        results = [self._info_from_content(x) for x in results]
        results.sort(lambda x, y: cmp(x['title'], y['title']))
        return results

    def _info_from_content(self, content):
        selectable = self._is_container_writable(content)
        i_am_context = IUUID(self.context) == content.uuid()

        result = {
                'key': content.uuid(),
                'id': content.getId(),
                'title': safe_unicode(content.Title()).encode('utf-8'),
                'tooltip': safe_unicode(content.Description()).encode('utf-8'),
                'icon': content.getIcon(),
                'noLink': True,
                'isFolder': True,
                'isLazy': True,
                'path': content.getPath(),
                'url': content.getURL(),
                'unselectable': not(selectable),
                'select': selectable and i_am_context,
                'children': [],
            }

        return result

    def _get_container_types(self):
        return ['Folder']

    def _is_container_writable(self, brain):
        '''True if the current user can write in the brain's container.

        NOTE: We need to access to the associate object, and this could
        be time consuming. In case of degradation of speed, check here.
        '''
        obj = brain.getObject()
        perm = getSecurityManager().checkPermission(
                        permissions.AddPortalContent, obj)
        return perm == 1
