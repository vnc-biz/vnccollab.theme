from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from plone.memoize.instance import memoize

from vnccollab.theme import messageFactory as _


DEFAULT_ITEMS_NUM = 10

# TODO: implement real IM (from mysql db) mix with other events
# TODO: implement regular (10 seconds) fetching
# TODO: implement reply form
# TODO: implement load replies 0 click
# TODO: implement updating of existing in stream messages


class StreamView(BrowserView):
    _template = ViewPageTemplateFile('templates/stream.pt')
    
    # methods to refer from zcml registrations
    
    def stream(self):
        return self._template()
    
    
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
        # TODO: implement real items fetching with 'since' and 'till' (for load
        # more functionality) dates
        result.extend(self._get_ims())
        result.extend(self._get_zmails())
        result.extend(self._get_news())
        # result.extend(self._get_rtickets())
        # TODO: recent should exclude news and comments
        # result.extend(self._get_recent())
        # result.extend(self._get_comments())
        
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
            {'id': 'im',
             'title': _(u"Instant Messages"),
             'desc': _(u"Show Only IM messages")},
            {'id': 'zm',
             'title': _(u"Mail"),
             'desc': _(u"Show Only Zimra Emails")},
            {'id': 'news',
             'title': _(u"News"),
             'desc': _(u"Show Only Cloud Portal News")},
            {'id': 'tickets',
             'title': _(u"Tickets"),
             'desc': _(u"Show Only Redmine Tickets")},
            {'id': 'recent',
             'title': _(u"Recent"),
             'desc': _(u"Show Only Recent Cloud Portal Updates")},
            {'id': 'comments',
             'title': _(u"Comments"),
             'desc': _(u"Show Only Cloud Portal Comments")}
        )
    
    # utility methods to work with different types of stream entries

    def _get_ims(self):
        """Returns list of instant messages"""
        result = []
        purl = self.purl()
        mtool = getToolByName(self.context, 'portal_membership')
        for brain in self._cp_items(('Document',), sort_on='created'):
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

    def _get_news(self):
        """Returns list of Cloud Portal News"""
        result = []
        purl = self.purl()
        for brain in self._cp_items(('News Item',), sort_on='created'):
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

    def _get_zmails(self):
        """Returns list of Cloud Portal News"""
        result = []
        purl = self.purl()
        for brain in self._cp_items(('Folder',), sort_on='created'):
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
                  limit=DEFAULT_ITEMS_NUM, extra_query={}):
        """Returns Cloud Portal (Plone) objects of given type"""
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        query = extra_query.copy()
        query['portal_type'] = ptypes
        if 'sort_on' not in query:
            query['sort_on'] = sort_on
        if 'sort_order' not in query:
            query['sort_order'] = sort_order
        if 'sort_limit' not in query:
            query['sort_limit'] = limit
        return catalog(**query)[:limit]

    @memoize
    def purl(self):
        return getToolByName(self.context, 'portal_url')()
