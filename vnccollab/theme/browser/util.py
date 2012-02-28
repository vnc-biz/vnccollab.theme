from BTrees.OOBTree import OOBTree
from persistent.dict import PersistentDict
from AccessControl import getSecurityManager

from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.utils import shasattr

from vnccollab.theme import messageFactory as _
from vnccollab.theme.config import PORTLETS_STATES_ANNO_KEY


class VNCCollabUtilView(BrowserView):
    """Utility views to call from templates"""
    
    def listFolderContentTypes(self):
        """Returns list of content types used inside
        current container.
        """
        items = []
            
        # calculate current folder's path
        cstate = getMultiAdapter((self.context, self.request),
            name='plone_context_state')
        path = '/'.join(cstate.folder().getPhysicalPath())
        
        # collect portal type list used withing current folder
        otypes = []
        catalog = getToolByName(self.context, 'portal_catalog')
        for brain in catalog(path={'query': path, 'depth': 1}):
            if brain.portal_type not in otypes:
                otypes.append(brain.portal_type)
        
        # prepare items list with type id and type title
        ttool = getToolByName(self.context, 'portal_types')
        for otype in otypes:
            item = {'id': otype, 'title': otype}
            if ttool is not None and shasattr(ttool, otype):
                item['title'] = _(safe_unicode(getattr(ttool, otype).Title()))
            items.append(item)
        
        # finally sort items and prepend 'All' filter element
        if len(items) > 0:
            items.sort(lambda x,y:cmp(x['title'], y['title']))
            items = [{'id': '', 'title': _(u'All')}] + items
        
        return tuple(items)

    def recordPortletState(self, hash, action, value):
        """Sets portlet state on site annotations"""
        # check if we got anthenticated user
        user = getSecurityManager().getUser()
        if not user or getattr(user, 'name', '') == 'Anonymous User':
            return _(u"No authenticated user found.")
        
        annotations = IAnnotations(self.context)
        users = annotations.get(PORTLETS_STATES_ANNO_KEY, None)
        if users is None:
            users = annotations[PORTLETS_STATES_ANNO_KEY] = OOBTree()
        
        userid = getattr(user, '_id', user.getId())
        portlets = users.get(userid, None)
        if portlets is None:
            portlets = users[userid] = PersistentDict()
        
        portlet = portlets.get(hash, None)
        if portlet is None:
            portlet = portlets[hash] = PersistentDict()
        
        portlet[action] = value
        
        return 'Done.'
