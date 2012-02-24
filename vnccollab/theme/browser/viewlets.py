from Acquisition import aq_base, aq_inner
from DateTime import DateTime

from zope.interface import alsoProvides
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.viewlet.interfaces import IViewlet

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IActionCategory, IAction
from Products.CMFCore.ActionInformation import ActionInfo
from Products.CMFPlone.utils import safe_unicode, normalizeString
from Products.CMFPlone.i18nl10n import monthname_msgid, weekdayname_msgid

from plone.app.viewletmanager.manager import BaseOrderedViewletManager
from plone.app.layout.viewlets import common
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.memoize.instance import memoize

from Products.Carousel.config import CAROUSEL_ID
from Products.Carousel.interfaces import ICarousel
from cioppino.twothumbs.rate import getTally
from vnccollab.theme import messageFactory as _
from vnccollab.theme.config import FOOTER_LINKS_CAT

_pl = MessageFactory('plonelocales')


class TopRatedViewlet(common.ViewletBase):
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

class ActionsListViewlet(common.ViewletBase):
    """Renders internal ActionsItem List object view.
    
    Gets first found ActionsItem List object in first level hierarchy.
    """
    
    def update(self):
        self.todo = None
        for obj in self.context.objectValues():
            if getattr(obj, 'portal_type', '') == 'ActionItemList':
                self.todo = obj
                break

class LoginViewlet(common.ViewletBase):
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

class HeaderTimeViewlet(common.ViewletBase):
    """Returns current date and time in local format"""

    def update(self):
        super(HeaderTimeViewlet, self).update()
        
        date = DateTime()
        self.day = date.day()
        self.month = _pl(monthname_msgid(int(date.strftime('%m'))),
            default=safe_unicode(date.Month()))
        self.dayname = _pl(weekdayname_msgid(int(date.strftime('%w'))),
            default=safe_unicode(date.DayOfWeek()))
        self.datetime = self.toLocalizedTime(date, long_format=True)
    
    def toLocalizedTime(self, time, long_format=None, time_only = None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                    domain='plonelocales')
        
class PathBarViewlet(common.PathBarViewlet):
    render = ViewPageTemplateFile('templates/path_bar.pt')

class FooterViewlet(common.FooterViewlet):
    index = ViewPageTemplateFile('templates/footer.pt')

    def update(self):
        super(FooterViewlet, self).update()
        self.columns = columns = {}
        
        context = aq_inner(self.context)
        actions_tool = getToolByName(context, 'portal_actions')
        
        # check if we got root category for all column links
        if not FOOTER_LINKS_CAT in actions_tool.objectIds():
            return
        
        # prepare expression context for evaluating TAL expressions
        ec = actions_tool._getExprContext(context)
        
        # go over root category and collect all sub-categories
        container = actions_tool[FOOTER_LINKS_CAT]
        cat_ids = container.objectIds()
        for cid in ('column1', 'column2', 'column3'):
            # skip not existing categories
            if cid not in cat_ids:
                continue
            
            cat = container[cid]
            if not IActionCategory.providedBy(cat):
                continue
            
            # prepare category actions
            actions = []
            for action in cat.objectValues():
                # look only for actions
                if not IAction.providedBy(action):
                    continue
                
                # create actioninfo object to compile and render TAL expressions
                # and check if action is available in current circumstances
                info = ActionInfo(action, ec)
                if not (info['visible'] and info['allowed'] and
                        info['available']):
                    continue
                
                # and finally extract all required details from action
                desc = action.getProperty('description', None) or None
                if desc is not None:
                    desc = _(safe_unicode(desc))
                actions.append({
                    'id': info['id'],
                    'title': _(safe_unicode(info['title'])),
                    'desc': desc,
                    'url': info['url']
                })
            
            # finally add category to be rendered as footer column
            columns[cid] = {
                'title': _(safe_unicode(cat.getProperty('title', ''))),
                'actions': tuple(actions)
            }
        
        self.columns = columns

class PersonalBarViewlet(common.PersonalBarViewlet):
    index = ViewPageTemplateFile('templates/personal_bar.pt')
    
    def update(self):
        super(PersonalBarViewlet, self).update()
        
        # get personal user image
        self.user_image = None
        if not self.anonymous:
            mtool = getToolByName(self.context, 'portal_membership')
            # if no userid passes it'll return portrait of logged in user
            portrait = mtool.getPersonalPortrait()
            if portrait is not None:
                self.user_image = portrait.absolute_url()

        # render languages viewlet
        context = aq_inner(self.context)
        languages = u''
        manager = BaseOrderedViewletManager()
        alsoProvides(manager, IPortalHeader)
        viewlet = queryMultiAdapter((context, self.request, self.view,
            manager), IViewlet, name='plone.app.i18n.locales.languageselector')
        if viewlet is not None:
            viewlet = viewlet.__of__(context)
            viewlet.update()
            languages = viewlet.render()
        self.languages = languages
