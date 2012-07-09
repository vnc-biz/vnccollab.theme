from Acquisition import aq_inner
from DateTime import DateTime

from zope.component import getMultiAdapter

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.AdvancedQuery import Eq, Between, Le, Ge, In

from plone.memoize.instance import memoize

from vnccollab.theme import messageFactory as _


DEFAULT_ITEMS_NUM = 10

# TODO: implement real IM (from mysql db) mix with other events
# TODO: implement reply form
# TODO: implement load replies 0 click
# TODO: implement updating of existing in stream messages


class StreamView(BrowserView):
    _template = ViewPageTemplateFile('templates/stream.pt')
    _template_macro = ViewPageTemplateFile('templates/stream_macro.pt')
    
    # methods to refer from zcml registrations
    
    @property
    def macros(self):
        """Returns page template macros"""
        return self._template.macros
    
    def stream(self):
        """Renders whole stream area"""
        return self._template()
    
    def check(self, since=None, till=None):
        """Used from ajax to check for specific stream items in time"""
        return self._template_macro(entries=self.get_items(since, till))
    
    # methods used by stream template
    
    def get_items(self, since=None, till=None):
        """Returns list of stream item sorted by date reversed, so that latest
        go first in the list.
        
        If given 'since' argument we return only those items updated since that
        date, not older. Otherwise we return first DEFAULT_ITEMS_NUM items.
        
        If give 'till', then we return first DEFAULT_ITEMS_NUM items that were
        updated/published before 'till' date.
        """
        result = []
        
        # convert dates
        if since is not None:
            since = DateTime(since)
        if till is not None:
            till = DateTime(till)
        
        # TODO: implement instant message tab
        # result.extend(self._get_ims(since=since, till=till))
        # TODO: implement zimbra mails tab
        # result.extend(self._get_zmails(since=since, till=till))
        result.extend(self._get_news(since=since, till=till))
        # TODO: implement redmine tickets tab
        # result.extend(self._get_rtickets())
        # TODO: include comments into recent items, after migration to
        #       p.a.discussion
        result.extend(self._get_recent(since=since, till=till))
        
        # sort items, latest - first
        result.sort(lambda x, y: cmp(x['datetime'], y['datetime']),
            reverse=True)
        
        return tuple(result)
        
    def get_item_types(self):
        """Returns list of stream item types"""
        return (
            {'id': 'all',
             'title': _(u"All"),
             'desc': _(u"Show All Items")},
            # {'id': 'im',
            #  'title': _(u"Instant Messages"),
            #  'desc': _(u"Show Only IM messages")},
            # {'id': 'zm',
            #  'title': _(u"Mail"),
            #  'desc': _(u"Show Only Zimra Emails")},
            {'id': 'news',
             'title': _(u"News"),
             'desc': _(u"Show Only Cloud Portal News")},
            # {'id': 'tickets',
            #  'title': _(u"Tickets"),
            #  'desc': _(u"Show Only Redmine Tickets")},
            {'id': 'recent',
             'title': _(u"Recent"),
             'desc': _(u"Show Only Recent Cloud Portal Updates")},
            # {'id': 'comments',
            #  'title': _(u"Comments"),
            #  'desc': _(u"Show Only Cloud Portal Comments")}
        )
    
    # utility methods to work with different types of stream entries

    def _get_ims(self, since=None, till=None):
        """Returns list of instant messages"""
        result = []
        purl = self.purl()
        mtool = getToolByName(self.context, 'portal_membership')
        
        # check if we got since and till arguments, if so - add it to catalog
        # query to get only recent or older items
        extra_query = None
        if since is not None:
            extra_query = Ge('created', since) & (~ Eq('created', since))
        elif till:
            extra_query = Le('created', till) & (~ Eq('created', till))
        
        for brain in self._cp_items(('Document',), sort_on='created',
            extra_query=extra_query):
            datetime = brain.created.toZone('GMT')
            time = datetime.strftime('%I:%M')
            date = datetime.strftime('%b %d, %Y')
            
            author = brain.Creator
            
            result.append({
                'type': 'im',
                'image': {'url': mtool.getPersonalPortrait(author
                    ).absolute_url(), 'alt': _(safe_unicode(author))},
                'url': '%s/author/%s' % (purl, author),
                'title': _(safe_unicode(author)),
                'date': date,
                'time': time,
                'datetime': datetime,
                'replies_num': 0,
                'can_reply': True,
                'body': _(safe_unicode(brain.Title))
            })
        return result

    def _get_news(self, since=None, till=None):
        """Returns list of Cloud Portal News"""
        result = []
        purl = self.purl()
        
        # check if we got since and till arguments, if so - add it to catalog
        # query to get only recent or older items
        extra_query = None
        if since is not None:
            extra_query = Ge('created', since) & (~ Eq('created', since))
        elif till:
            extra_query = Le('created', till) & (~ Eq('created', till))
        
        for brain in self._cp_items(('News Item',), sort_on='created',
            extra_query=extra_query):
            datetime = brain.created.toZone('GMT')
            time = datetime.strftime('%I:%M')
            date = datetime.strftime('%b %d, %Y')
            
            result.append({
                'type': 'news',
                'image': {
                    'url': '%s/add_content_area/metabox_icon_news-item.png' %
                    purl, 'alt': _(u"NEWS")},
                'url': brain.getURL(),
                'title': _(u"NEWS"),
                'date': date,
                'time': time,
                'datetime': datetime,
                'replies_num': 0,
                'can_reply': True,
                'body': _(safe_unicode(brain.Title))
            })
        return result

    def _get_recent(self, since=None, till=None):
        """Returns list of Recently updated content and comments on the site"""
        result = []
        purl = self.purl()
        
        # check if we got since and till arguments, if so - add it to catalog
        # query to get only recent or older items
        extra_query = None
        if since is not None:
            extra_query = Ge('modified', since) & (~ Eq('modified', since))
        elif till:
            extra_query = Le('modified', till) & (~ Eq('modified', till))
        
        # get friendly content types
        portal_state = getMultiAdapter((self.context, self.request),
            name=u'plone_portal_state')
        ftypes = list(portal_state.friendly_types())
        ftypes.remove('News Item')
        
        for brain in self._cp_items(ftypes, sort_on='modified',
            extra_query=extra_query):
            datetime = brain.modified.toZone('GMT')
            time = datetime.strftime('%I:%M')
            date = datetime.strftime('%b %d, %Y')
            
            result.append({
                'type': 'recent',
                'image': {
                    'url': '%s/add_content_area/' \
                        'metabox_icon_serviceportal.png' % purl,
                    'alt': _(u"RECENT")},
                'url': brain.getURL(),
                'title': _(u"RECENT"),
                'date': date,
                'time': time,
                'datetime': datetime,
                'replies_num': 0,
                'can_reply': True,
                'body': _(safe_unicode(brain.Title))
            })
        return result

    def _get_zmails(self, since=None, till=None):
        """Returns list of Cloud Portal News"""
        result = []
        purl = self.purl()
        
        # check if we got since and till arguments, if so - add it to catalog
        # query to get only recent or older items
        extra_query = None
        if since is not None:
            extra_query = Ge('created', since) & (~ Eq('created', since))
        elif till:
            extra_query = Le('created', till) & (~ Eq('created', till))
        
        for brain in self._cp_items(('Folder',), sort_on='created',
            extra_query=extra_query):
            datetime = brain.created.toZone('GMT')
            time = datetime.strftime('%I:%M')
            date = datetime.strftime('%b %d, %Y')
            
            result.append({
                'type': 'zm',
                'image': {
                    'url': '%s/add_content_area/metabox_icon_email.png' %
                    purl, 'alt': _(u"MAIL")},
                # TODO: link to dedicated zimbra email view
                'url': 'https://zcs.vnc.biz/zimbra/h/search',
                'title': _(u"MAIL"),
                'date': date,
                'time': time,
                'datetime': datetime,
                'replies_num': 0,
                'can_reply': True,
                'body': _(safe_unicode(brain.Title))
            })
        return result

    def _cp_items(self, ptypes, sort_on='modified', sort_order='reverse',
                  limit=DEFAULT_ITEMS_NUM, extra_query=None):
        """Returns Cloud Portal (Plone) objects of given type"""
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        query = In('portal_type', ptypes)
        
        if extra_query is not None:
            query &= extra_query
        
        if sort_order == 'reverse':
            sort_order = 'desc'
        else:
            sort_order = 'asc'

        return catalog.evalAdvancedQuery(query, ((sort_on,
            sort_order),))[:limit]

    @memoize
    def purl(self):
        return getToolByName(self.context, 'portal_url')()
