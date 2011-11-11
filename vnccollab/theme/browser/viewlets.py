from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, normalizeString

from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

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

class ActionsListViewlet(ViewletBase):
    """Renders internal ActionsItem List object view.
    
    Gets first found ActionsItem List object in first level hierarchy.
    """
    
    def update(self):
        self.todo = None
        for obj in self.context.objectValues():
            if getattr(obj, 'portal_type', '') == 'ActionItemList':
                self.todo = obj
                break

class LoginViewlet(ViewletBase):
    """Most methods are copied over from login portlet renderer"""
    
    def __init__(self, *args, **kw):
        super(LoginViewlet, self).__init__(*args, **kw)

        self.membership = getToolByName(self.context, 'portal_membership')
        self.context_state = getMultiAdapter((self.context, self.request),
            name=u'plone_context_state')
        self.portal_state = getMultiAdapter((self.context, self.request),
            name=u'plone_portal_state')
        self.pas_info = getMultiAdapter((self.context, self.request),
            name=u'pas_info')

    def show(self):
        if not self.portal_state.anonymous():
            return False
        if not self.pas_info.hasLoginPasswordExtractor():
            return False
        page = self.request.get('URL', '').split('/')[-1]
        return page not in ('login_form', '@@register')

    @property
    def available(self):
        return self.auth() is not None and self.show()

    def login_form(self):
        return '%s/login_form' % self.portal_state.portal_url()

    def mail_password_form(self):
        return '%s/mail_password_form' % self.portal_state.portal_url()

    def login_name(self):
        auth = self.auth()
        name = None
        if auth is not None:
            name = getattr(auth, 'name_cookie', None)
        if not name:
            name = '__ac_name'
        return name

    def login_password(self):
        auth = self.auth()
        passwd = None
        if auth is not None:
            passwd = getattr(auth, 'pw_cookie', None)
        if not passwd:
            passwd = '__ac_password'
        return passwd

    def join_action(self):
        context = self.context
        tool = getToolByName(context, 'portal_actions')
        join = tool.listActionInfos(action_chain='user/join', object=context)
        if len(join) > 0:
            return join[0]['url']
        return None

    def can_register(self):
        if getToolByName(self.context, 'portal_registration', None) is None:
            return False
        return self.membership.checkPermission('Add portal member',
            self.context)

    def can_request_password(self):
        return self.membership.checkPermission('Mail forgotten password',
            self.context)

    @memoize
    def auth(self, _marker=[]):
        acl_users = getToolByName(self.context, 'acl_users')
        return getattr(acl_users, 'credentials_cookie_auth', None)
