import time
import sys
from urllib2 import urlopen, Request
import logging
import base64
import simplejson
from datetime import datetime
from pyactiveresource.activeresource import ActiveResource

from DateTime import DateTime

from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements, Interface
from zope import schema

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from vnccollab.theme.portlets.zimbra_mail import logException
from vnccollab.theme import messageFactory as _

logger = logging.getLogger('vnccollab.theme.RedmineTicketsPortlet')


class IRedmineTicketsPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Header"),
        description=_(u"Header of the portlet."),
        required=True,
        default=u'Redmine Tickets')

    url = schema.URI(
        title=_(u"Redmine URL"),
        description=_(u"Root url to your Redmine service."),
        required=True,
        default='https://redmine.vnc.biz/redmine')

    # plone_related = schema.Bool(
    #     title=_(u"List Plone Related tickets"),
    #     description=_(u"If checked, only tickets related to Plone Content "
    #         "objects  will be listed in a portlet. NOT IMPLEMENTED YET."),
    #     required=False,
    #     default=False)

    count = schema.Int(
       title=_(u"Number of items to display"),
       description=_(u"How many items to list."),
       required=True,
       default=5)
    
    username = schema.ASCIILine(
        title=_(u"Username"),
        description=_(u"If not set, redmine_username property of authenticated "
                      "user will be used."),
        required=False,
        default='')

    password = schema.Password(
        title=_(u"Password"),
        description=_(u"If not set, redmine_password property of authenticated "
                      "user will be used."),
        required=False,
        default=u'')

    request_timeout = schema.Int(
        title=_(u"Request timeout"),
        description=_(u"How many seconds to wait for hanging Redmine request."),
        required=True,
        default=15)

class Assignment(base.Assignment):
    implements(IRedmineTicketsPortlet)

    header = u''
    url = ''
    plone_related = False
    count = 5
    username = ''
    password = u''
    request_timeout = 15

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=u'', url='https://redmine.vnc.biz/redmine',
                 plone_related=False, count=5, username='', password=u'',
                 request_timeout=15):
        self.header = header
        self.url = url
        self.plone_related = plone_related
        self.count = count
        self.username = username
        self.password = password
        self.request_timeout = request_timeout

class Renderer(base.Renderer):

    render = ZopeTwoPageTemplateFile('templates/redmine_tickets.pt')

    @property
    def available(self):
        return len(self.getTickets()) > 0

    def getTicketsURL(self):
        """Returns tickets root url"""
        return '%s/issues' % self.data.url
        
    def getTickets(self):
        """Returns list of opened issues for authenticated user"""
        username, password = self.getAuthCredentials()
        if not username or not password:
            return ()
        
        return self._tickets(self.data.url, username, password)

    @memoize
    def _tickets(self, url, username, password):
        """Requests redmine for list of opened issues for current user"""
        # create ActiveResource classes to fetch data from Redmine over REST API
        attrs = {'_site': url, '_user': username, '_password': password}
        if self.data.request_timeout:
            attrs['_timeout'] = self.data.request_timeout
        
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
            return ()
        
        lt = getToolByName(self.context, 'translation_service').ulocalized_time
        plone_view = getMultiAdapter((self.context, self.request),
            name=u'plone')
        
        # process retrieved data
        tickets = []
        limit = self.data.count
        counter = 0
        for item in data:
            # we've got enough tickets
            if counter >= limit:
                break
            
            info = item.to_dict()
            
            # skip invalid entries
            if not info.get('id') or not info.get('subject'):
                continue
            
            # prepare date
            date = info.get('updated_on', '')
            if date:
                date = plone_view.toLocalizedTime(date, long_format=1)
            
            # prepare ticket body
            body = safe_unicode(info.get('description', ''))
            if body:
                # crop length to 160 characters
                body = plone_view.cropText(body, 160, ellipsis=u'...')
            
            tickets.append({
                'id': info['id'],
                'title': safe_unicode(info['subject']),
                'body': body,
                'date': date,
                'url': '%s/issues/%s' % (url, info['id'])
            })
            
            counter += 1
        
        return tuple(tickets)

    @memoize
    def getAuthCredentials(self):
        """Returns username and password for zimbra user."""
        username, password = self.data.username, self.data.password
        if not (username and password): 
            # take username and password from authenticated user Zimbra creds
            mtool = getToolByName(self.context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            username, password = member.getProperty('redmine_username', ''), \
                member.getProperty('redmine_password', '')
        # password could contain non-ascii chars, ensure it's properly encoded
        return username, safe_unicode(password).encode('utf-8')

    @property
    def title(self):
        """return title of feed for portlet"""
        return self.data.header

class AddForm(base.AddForm):
    form_fields = form.Fields(IRedmineTicketsPortlet)
    label = _(u"Add Redmine Tickets Portlet")
    description = _(u"Renders list of opened Redmine Tickets for authenticated "
        "user.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IRedmineTicketsPortlet)
    label = _(u"Edit Redmine Tickets Portlet")
    description = _(u"Renders list of opened Redmine Tickets for authenticated "
        "user.")
