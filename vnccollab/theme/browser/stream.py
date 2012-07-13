import logging
from pyactiveresource.activeresource import ActiveResource

from Acquisition import aq_inner
from DateTime import DateTime

from zope.component import getMultiAdapter, getUtility

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.AdvancedQuery import Eq, Between, Le, Ge, In

from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry

from jarn.xmpp.core.interfaces import IPubSubStorage, INodeEscaper

from vnccollab.theme.util import getZimbraUrl
from vnccollab.theme.zimbrautil import IZimbraUtil
from vnccollab.theme import messageFactory as _
from vnccollab.theme.portlets.zimbra_mail import logException


logger = logging.getLogger('vnccollab.theme.VNCStream')

DEFAULT_ITEMS_NUM = 20

# TODO: implement subscriptions fetching for user node in IM tab
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
    
    def check(self, since=None, till=None, uid=None):
        """Used from ajax to check for specific stream items in time"""
        return self._template_macro(entries=self.get_items(since, till, uid))
    
    # methods used by stream template
    
    def get_user_data(self, userid=''):
        """Returns user name, url and image.
        
        If not given userid, return data of authenticated user.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        purl = self.purl()
        
        if userid:
            member = mtool.getMemberById(userid)
        else:
            member = mtool.getAuthenticatedMember()
        
        name = userid
        if member:
            userid = member.getId()
            name = member.getProperty('fullname') or userid
        
        escaper = getUtility(INodeEscaper)
        return {'name': _(safe_unicode(name)),
                'url': '%s/author/%s' % (purl, userid),
                'image': mtool.getPersonalPortrait(userid).absolute_url(),
                'id': userid,
                'safe_id': escaper.escape(userid)}
    
    def get_items(self, since=None, till=None, uid=None):
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
        
        result.extend(self._get_ims(since=since, till=till))
        result.extend(self._get_zmails(since=since, till=till, uid=uid))
        result.extend(self._get_news(since=since, till=till, uid=uid))
        result.extend(self._get_rtickets(since=since, till=till, uid=uid))
        # TODO: include comments into recent items, after migration to
        #       p.a.discussion
        result.extend(self._get_recent(since=since, till=till, uid=uid))
        
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
        )
    
    # utility methods to work with different types of stream entries

    def _get_ims(self, since=None, till=None, uid=None):
        """Returns list of instant messages"""
        result = []
        purl = self.purl()
        mtool = getToolByName(self.context, 'portal_membership')
        storage = getUtility(IPubSubStorage)
        escaper = getUtility(INodeEscaper)
        convert = getToolByName(self, 'portal_transforms').convert
        
        # go over recent messages
        for item in storage.itemsFromNodes(['people'], start=0,
            count=DEFAULT_ITEMS_NUM):
            
            # TODO: handle comments
            if item.get('parent'):
                continue
            
            datetime = DateTime(item['updated']).toZone('GMT')
            
            # TODO: handle till argument
            if since and since >= datetime:
                # we've got too old entry, break from the loop
                break
            
            fullname = author = item['author']
            if author:
                author = escaper.unescape(author)
                member = mtool.getMemberById(author)
                if member:
                    fullname = member.getProperty('fullname', None) or author
                else:
                    fullname = author
            
            # strip down html code from message body
            body = safe_unicode(item['content']).encode('utf-8')
            body = safe_unicode(convert('html_to_text', body).getData())
            
            result.append({
                'uid': item['id'],
                'type': 'im',
                'image': {'url': mtool.getPersonalPortrait(author
                    ).absolute_url(), 'alt': _(safe_unicode(author))},
                'url': '%s/@@pubsub-feed?node=%s' % (purl, author),
                'title': _(safe_unicode(fullname)),
                'date': datetime.strftime('%b %d, %Y'),
                'time': datetime.strftime('%I:%M'),
                'datetime': datetime,
                'replies_num': 0,
                'can_reply': True,
                'body': body
            })
        
        return result

    def _get_news(self, since=None, till=None, uid=None):
        """Returns list of Cloud Portal News"""
        result = []
        purl = self.purl()
        
        # check if we got since and till arguments, if so - add it to catalog
        # query to get only recent or older items
        extra_query = None
        limit = DEFAULT_ITEMS_NUM
        if since is not None:
            limit = None
            extra_query = Ge('created', since) & (~ Eq('created', since))
        elif till:
            extra_query = Le('created', till) & (~ Eq('created', till))
        
        for brain in self._cp_items(('News Item',), sort_on='created',
            extra_query=extra_query, limit=limit):
            datetime = brain.created.toZone('GMT')
            time = datetime.strftime('%I:%M')
            date = datetime.strftime('%b %d, %Y')
            
            result.append({
                'uid': brain.UID,
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

    def _get_recent(self, since=None, till=None, uid=None):
        """Returns list of Recently updated content and comments on the site"""
        result = []
        purl = self.purl()
        
        # check if we got since and till arguments, if so - add it to catalog
        # query to get only recent or older items
        extra_query = None
        limit = DEFAULT_ITEMS_NUM
        if since is not None:
            limit = None
            extra_query = Ge('modified', since) & (~ Eq('modified', since))
        elif till:
            extra_query = Le('modified', till) & (~ Eq('modified', till))
        
        # get friendly content types
        portal_state = getMultiAdapter((self.context, self.request),
            name=u'plone_portal_state')
        ftypes = list(portal_state.friendly_types())
        ftypes.remove('News Item')
        
        for brain in self._cp_items(ftypes, sort_on='modified',
            extra_query=extra_query, limit=limit):
            datetime = brain.modified.toZone('GMT')
            time = datetime.strftime('%I:%M')
            date = datetime.strftime('%b %d, %Y')
            
            result.append({
                'uid': brain.UID,
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

    def _get_rtickets(self, since=None, till=None, uid=None):
        """Returns list of Redmine tickets belonging to currently logged in
        user.
        
        If since or till are passed, then return tickets that suit given date
        range.
        """
        result = []
        purl = self.purl()
        
        # get redmine credentials
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        username, password = member.getProperty('redmine_username', ''), \
            member.getProperty('redmine_password', '')
        if not (username and password):
            return []
        else:
            password = safe_unicode(password).encode('utf-8')
        
        # get redmine url
        url = getUtility(IRegistry).get('vnccollab.theme.redmine.url')
        if not url:
            return []
        
        # create ActiveResource classes to fetch data from Redmine over REST API
        attrs = {'_site': url, '_user': username, '_password': password}
        
        Issue = type("Issue", (ActiveResource,), attrs.copy())
        User = type("User", (ActiveResource,), attrs.copy())
        
        # do actual calls to redmine
        try:
            # fetch opened issues belonging to authenticated user
            data = Issue.find(assigned_to_id=User.find('current').id,
             status_id='o', sort='updated_on:desc')
        except Exception, e:
            logException(_(u"Error during fetching redmine tickets %s" % url),
                context=self.context, logger=logger)
            return []
        
        # cut down number of tickets in case we don't have date range arguments
        if not since:
            data = data[:DEFAULT_ITEMS_NUM]
        
        for item in data:
            info = item.to_dict()
            
            # skip invalid entries
            if not info.get('id') or not info.get('subject'):
                continue
            
            # prepare date
            datetime = DateTime(info.get('updated_on', '')).toZone('GMT')
            # TODO: handle till argument
            if since and since >= datetime:
                # we've got too old entry, break from the loop
                break
            
            result.append({
                'uid': info['id'],
                'type': 'tickets',
                'image': {
                    'url': '%s/add_content_area/metabox_icon_task.png' % purl,
                    'alt': _(u"ISSUE")},
                'url': '%s/issues/%s' % (url, info['id']),
                'title': _(u"ISSUE"),
                'date': datetime.strftime('%b %d, %Y'),
                'time': datetime.strftime('%I:%M'),
                'datetime': datetime,
                'replies_num': 0,
                'can_reply': True,
                'body': _(safe_unicode(info['subject']))
            })
        
        return result

    def _get_zmails(self, since=None, till=None, uid=None):
        """Returns list of recent zimbra emails."""
        purl = self.purl()
        
        # get zimbra settings
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        username = member.getProperty('zimbra_username', '')
        password = member.getProperty('zimbra_password', '')
        if not (username and password):
            return []
        
        # make zimbra soap query to get list of recent emails
        try:
            zimbra = getUtility(IZimbraUtil).get_client(username=username,
                password=password)
            mails = zimbra.get_emails(folder='inbox', limit=DEFAULT_ITEMS_NUM,
                types='message')
        except Exception, e:
            logException(_(u"Error during fetching zimbra mails"),
                context=self.context, logger=logger)
            return []
        
        zurl = getZimbraUrl(self.context)
        result = []
        for mail in mails:
            # TODO: handle till argument
            datetime = DateTime(int(mail['date'])/1000).toZone('GMT')
            if since and since >= datetime:
                # we've got too old entry, break from the loop
                break
            
            result.append({
                'uid': mail['id'],
                'type': 'zm',
                'image': {
                    'url': '%s/add_content_area/metabox_icon_email.png' %
                    purl, 'alt': _(u"MAIL")},
                'url': '%s/zimbra/h/search?st=conversation&id=%s' \
                    '&action=view&cid=%s' % (zurl, mail['id'],
                    mail['cid']),
                'title': _(u"MAIL"),
                'date': datetime.strftime('%b %d, %Y'),
                'time': datetime.strftime('%I:%M'),
                'datetime': datetime,
                'replies_num': 0,
                'can_reply': True,
                'body': mail['subject']
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
        
        result = catalog.evalAdvancedQuery(query, ((sort_on, sort_order),))
        
        # apply limit if required
        if limit:
            result = result[:limit]
        
        return result

    @memoize
    def purl(self):
        return getToolByName(self.context, 'portal_url')()
