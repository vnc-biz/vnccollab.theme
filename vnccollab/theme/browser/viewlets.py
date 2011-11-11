from Acquisition import aq_base
from DateTime import DateTime

from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, normalizeString
from Products.CMFPlone.i18nl10n import monthname_msgid, weekdayname_msgid

from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from Products.Carousel.config import CAROUSEL_ID
from Products.Carousel.browser.viewlet import CarouselViewlet
from Products.Carousel.interfaces import ICarousel
from cioppino.twothumbs.rate import getTally
from vnccollab.theme import messageFactory as _

_pl = MessageFactory('plonelocales')


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

class HeaderTimeViewlet(ViewletBase):
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

class HomePageCarouselViewlet(CarouselViewlet):
    """Always displays root site /carousel's banners"""
    
    def update(self):
        """
        Set the variables needed by the template.
        """
        
        self.available = False
        
        context_state = self.context.restrictedTraverse('@@plone_context_state')
        folder = getToolByName(self.context, 'portal_url').getPortalObject()
                
        if hasattr(aq_base(folder), CAROUSEL_ID):
            carousel = ICarousel(folder[CAROUSEL_ID], None)
            if not carousel:
                return
        else:
            return
        
        settings = carousel.getSettings()
        
        if not settings.enabled:
            return
        
        banners = carousel.getBanners()
        if not banners:
            return

        self.banners = self._template_for_carousel(
            settings.banner_template or u'@@banner-default',
            carousel
        )
        
        self.pager = self._template_for_carousel(
            settings.pager_template or u'@@pager-numbers',
            carousel
        )
        
        width, height = banners[0].getSize()
        self.height = settings.height or height or 0
        self.width = settings.width or width or 0
        self.transition = settings.transition_type
        self.speed = int(settings.transition_speed * 1000)
        self.delay = int(settings.transition_delay * 1000)
        self.element_id = settings.element_id
        self.available = True
