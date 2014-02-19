import simplejson

from Acquisition import aq_parent
from AccessControl import getSecurityManager

from zope.component import getMultiAdapter

from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot, IFolderish
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.uuid.interfaces import IUUID
from plone.app.search.browser import Search
from plone.app.contentlisting.interfaces import IContentListing


class GetTreeJson(BrowserView):
    '''Returns a JSON representation of the directory structure
       to be used by jquery.dynatree library.'''
    CONTENT_SEARCH_HTML = ViewPageTemplateFile('templates/content_search.pt')

    def getSearchDestinationList(self):
        """ Return list of destinatons """
        #if type_ is None:
        #    type_ = self.request.get('type_', None)

        catalog = getToolByName(self.context, 'portal_catalog')

        container_path = ''
        #if uid is not None:
        #    container = catalog(UID=uid)
        #    if len(container) == 1:
        #        container = container[0]
        #        container_path = container.getPath()

        #if not container_path:
        portal = api.portal.get()
        container_path = '/'.join(portal.getPhysicalPath())

        query = {'portal_type': self._get_container_types(),
                 'path': {'query': container_path}}

        results = IContentListing(catalog(**query))
        results = [self._info_from_content(x) for x in results]
        results.sort(lambda x, y: cmp(x['title'], y['title']))
        return results

        """#return simplejson.dumps([])
        search = Search(self.context, self.request)
        query = dict(SearchableText=self.request.get('SearchableText', ''),
                     #title=self.request.get('SearchableText', ''),
                     portal_type=self._get_container_types())
        results = [self._info_from_content(x, search_html=True)
                    for x in search.results(query, batch=False)]
        results.sort(lambda x, y: cmp(x['title'], y['title']))
        return simplejson.dumps(results)"""

    def getInitialTree(self):
        '''Returns the initial tree for the dynatree.'''
        context = self.getFolderishParent(self.context)
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

        root_node = self.getRootNode()
        root_node['children'] = tree
        return simplejson.dumps(root_node)

    def getRootNode(self):
        portal = api.portal.get()
        tree = self._info_from_content(portal)
        return tree

    def getFolderishParent(self, obj):
        '''Returns obj or its nearest parent that is folderish.'''
        while True:
            if IFolderish.providedBy(obj):
                return obj
            obj = aq_parent(obj)

    def _insert_child_tree(self, tree, child_tree, child_uid):
        for branch in tree:
            if branch.get('key', False) == child_uid:
                branch['children'] = child_tree
                branch['isLazy'] = False
                branch['expand'] = True

    def getTree(self, uid=None, type_=None):
        '''Returns the (lazy) tree for a given node.

           params:
               uid: UUID of the container to get its tree.
        '''
        results = self.get_tree(uid=uid)
        return simplejson.dumps(results)

    def get_tree(self, uid=None, type_=None):
        if type_ is None:
            type_ = self.request.get('type_', None)

        catalog = getToolByName(self.context, 'portal_catalog')

        container_path = ''
        if uid is not None:
            container = catalog(UID=uid)
            if len(container) == 1:
                container = container[0]
                container_path = container.getPath()

        if not container_path:
            portal = api.portal.get()
            container_path = '/'.join(portal.getPhysicalPath())

        query = {'portal_type': self._get_container_types(),
                 'path': {'query': container_path, 'depth': 1}}

        results = IContentListing(catalog(**query))
        results = [self._info_from_content(x, type_) for x in results]
        results.sort(lambda x, y: cmp(x['title'], y['title']))
        return results

    def _info_from_content(self, content, type_=None, search_html=False):
        breadcrumbs_view = getMultiAdapter((content.getObject(), self.request),
                                           name='breadcrumbs_view')
        breadcrumbs = breadcrumbs_view.breadcrumbs()
        content_is_root = ISiteRoot.providedBy(content)
        if content_is_root:
            content_uid = '0'
            obj = content
            path = content.absolute_url_path()
            url = content.absolute_url()
        else:
            obj = content.getObject()
            path = content.getPath()
            url = content.getURL()
            content_uid = content.uuid()

        selectable = self._is_container_selectable(obj, type_)
        context = self.getFolderishParent(self.context)
        context_is_root = ISiteRoot.providedBy(context)
        if context_is_root:
            context_uid = '0'
        else:
            context_uid = IUUID(context)

        i_am_context = context_uid == content_uid

        result = {
            'key': content_uid,
            'id': content.getId(),
            'title': safe_unicode(content.Title()).encode('utf-8'),
            'tooltip': safe_unicode(content.Description()).encode('utf-8'),
            'icon': content.getIcon(),
            'noLink': True,
            'isFolder': True,
            'isLazy': True,
            'path': path,
            'url': url,
            'unselectable': not(selectable),
            'activate': selectable and i_am_context,
            'children': [],
            'breadcrumbs': breadcrumbs,
        }
        if search_html:
            result['search_html'] = self.CONTENT_SEARCH_HTML(entry=result)

        return result

    def _get_container_types(self):
        return ['Folder']

    def _is_container_selectable(self, container, type_):
        writable = self._is_container_writable(container)
        if not writable:
            return False
        return self._is_type_allowed_in_container(container, type_)

    def _is_type_allowed_in_container(self, obj, type_):
        if type_ is None:
            return True

        allowed_types = list(obj.getLocallyAllowedTypes())
        return type_ in allowed_types

    def _is_container_writable(self, obj):
        '''True if the current user can write in the object container.

        NOTE: We need to access to the associate object, and this could
        be time consuming. In case of degradation of speed, check here.
        '''
        perm = getSecurityManager().checkPermission(
            permissions.AddPortalContent, obj)
        return perm == 1
