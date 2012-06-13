from datetime import datetime

from zope.interface import Interface, implements
from zope.component import getUtility, getMultiAdapter, queryMultiAdapter

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager, IPortletRenderer
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize

from vnccollab.theme.zimbrautil import IZimbraUtil
from vnccollab.theme.browser.zimbra import ZimbraMailPortletView
from vnccollab.theme.portlets import redmine_tickets
from vnccollab.theme import messageFactory as _


class Dashlet(BrowserView):

    #dashlet = ViewPageTemplateFile('templates/dashlet.pt')
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.count = int(request.get('count', '5'))
        self.type_ = request.get('type', 'all')

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                name=u'plone_portal_state')
        self.portal_state = portal_state
        self.friendlyTypes = portal_state.friendly_types()


    def items(self):
        type_ = self.type_
        if type_ == 'all':
            items = self.all_items()
        elif type_ == 'mails':
            items =  self.all_mails()
        elif type_ == 'news':
            items =  self.all_news()
        elif type_ == 'recent':
            items = self.all_recents()
        elif type_ == 'tickets':
            items = self.all_tickets()
        else:
            items = []
        return items


    def all_items(self):
        """Return the last Tickets, Mails, News and Items"""
        # We'll try to get at least self.data.count elements of each type
        # so when we filter by type we have enough entries to show.
        items = self.all_news()
        items.extend(self.all_recents())
        items.extend(self.all_tickets())
        items.extend(self.all_mails())
        items.sort(lambda x, y: cmp(x.Date, y.Date), reverse=True)
        items = self._remove_repeated(items)
        return items[:self.count]

    def _remove_repeated(self, items):
        urls = []
        uniques = []
        for item in items:
            url = item.getURL()
            if url not in urls:
                urls.append(url)
                uniques.append(item)
        return uniques

    def all_news(self):
        return self.all_by_types('News Item')

    def all_recents(self):
        return self.all_by_types(self.friendlyTypes)

    def all_tickets(self):
        renderer = self._get_redmine_ticket_portlet()
        tickets = renderer.getTickets()
        tickets = [FakeTicketBrain(ticket) for ticket in tickets]
        return tickets

    @memoize
    def _get_redmine_ticket_portlet(self):
        context = aq_inner(self.context)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                context=portal)
        assignment = redmine_tickets.Assignment(count=self.count)
        renderer = queryMultiAdapter((context, self.request, self,
                manager, assignment), IPortletRenderer)
        renderer.update()
        return renderer

    @memoize
    def all_mails(self):
        '''
        zimbra = ZimbraMailPortletView(self.context, self.request)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        username, password = member.getProperty('zimbra_username', ''), \
            member.getProperty('zimbra_password', '')
        data = {
            'url' : 'https://zcs.vnc.biz',
            'username' : username,
            'password' : password,
            }
        '''
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        username = member.getProperty('zimbra_username', '')
        password = member.getProperty('zimbra_password', '')
        zimbraUtil = getUtility(IZimbraUtil)
        try:
            client = zimbraUtil.get_client(username=username, password=password)
            mails = client.get_emails(limit=self.count)
        except:
            mails = []
        return [FakeMailBrain(mail) for mail in mails][:self.count]

    def all_by_types(self, portal_types):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        path = self.portal_state.navigation_root_path()
        limit = self.count
        return catalog(portal_type=portal_types,
                       path=path,
                       sort_on='Date',
                       sort_order='reverse',
                       sort_limit=limit)[:limit]


class FakeTicketBrain:
    '''Wrapper for redmine ticket implementing the minimum attributes
    of brains.'''
    def __init__(self, dct):
        self.id = dct.get('id', '')
        self.url = dct.get('url', '')
        self.Title = dct.get('title', '')
        date = datetime.strptime(dct['date'], '%b %d, %Y %I:%M %p')
        self.Date = date.isoformat()
        self.portal_type = 'Redmine Ticket'
        # html -> plain text
        portal_transforms = getToolByName(self, 'portal_transforms')
        html_body = dct.get('body', '')
        html_body = html_body.encode() if html_body is not None else u''
        txt_body = portal_transforms.convert('html_to_text', html_body).getData()
        self.Description = txt_body

    @property
    def pretty_title_or_id(self):
        if self.Title:
            return self.Title
        else:
            return self.id

    def getURL(self):
        return self.url

class FakeMailBrain:
    '''Wrapper for zimbra mail implementing the minimum attributes
    of brains.'''
    def __init__(self, dct):
        self.id = dct.get('id', '')
        self.url = dct.get('url', '')
        self.Title = dct.get('subject', '')
        # TODO: html -> plain text
        self.Description = dct.get('body', '')
        date = datetime.fromtimestamp(int(dct['date'])/1000)
        self.Date = date.isoformat()
        self.portal_type = 'Mail'

    @property
    def pretty_title_or_id(self):
        if self.Title:
            return self.Title
        else:
            return self.id

    def getURL(self):
        return self.url

