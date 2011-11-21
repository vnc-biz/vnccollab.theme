import time
import sys
from urllib2 import urlopen, Request
import logging
import base64
import simplejson
from datetime import datetime

from DateTime import DateTime


from zope.formlib import form
from zope.interface import implements, Interface
from zope import schema

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFPlone.utils import safe_unicode

from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from vnccollab.theme import messageFactory as _


ZIMBRA_MAIL_URL_PAT = '%(url)s/home/%(username)s/%(folder_id)s?fmt=json'

# store the json data here (which means in RAM)
JSON_DATA = {}  # url: data

logger = logging.getLogger('vnccollab.theme.ZimbraMailPortlet')
def logException(msg, context=None):
    logger.exception(msg)
    if context is not None:
        error_log = getattr(context, 'error_log', None)
        if error_log is not None:
            error_log.raising(sys.exc_info())

class IJSONObject(Interface):

    def __init__(url, timeout, username=None, password=None,
                 request_timeout=None, failure_delay=5):
        """Initialize the json object with the given url.
        
        Will not automatically load it.
        Timeout defines the time between updates in minutes.
        """

    def loaded():
        """Return if this json object is in a loaded state"""

    def data():
        """Return the data of the json object"""

    def last_update_time_in_minutes():
        """Return the time this json object was last updated in minutes since
        epoch"""

    def last_update_time():
        """Return the time the json object was last updated as DateTime
        object
        """

    def needs_update():
        """Return if this json object needs to be updated"""

    def update():
        """Update this json object.
        
        Will automatically check failure state etc.
        Returns True or False whether it succeeded or not
        """

    def update_failed():
        """Return if the last update failed or not"""

    def ok():
        """Is this json object ok to display?"""

class JSONObject(object):
    """JSON Object"""
    implements(IJSONObject)

    def __init__(self, context, url, timeout, username=None, password=None,
                 request_timeout=None, failure_delay=5):
        self.context = context
        self.url = url
        self._timeout = timeout

        self._data = None
        self._loaded = False    # is the json object loaded
        self._failed = False    # does it fail at the last update?
        self._last_update_time_in_minutes = 0 # when was the json last updated?
        self._last_update_time = None        # time as DateTime or None
        self._request_timeout = request_timeout # request timeout in seconds
        self._failure_delay = failure_delay  # time in minutes before retry to
                                             # load json after a failure
        
        # auth credentials for Basic Auth method
        self.username = username
        self.password = password

    @property
    def last_update_time_in_minutes(self):
        """See interface"""
        return self._last_update_time_in_minutes

    @property
    def last_update_time(self):
        """See interface"""
        return self._last_update_time

    @property
    def update_failed(self):
        """See interface"""
        return self._failed

    @property
    def ok(self):
        """See interface"""
        return (not self._failed and self._loaded)

    @property
    def loaded(self):
        """See interface"""
        return self._loaded

    @property
    def needs_update(self):
        """See interface"""
        now = time.time() / 60
        return (self.last_update_time_in_minutes + self._timeout) < now

    def update(self):
        """See interface"""
        now = time.time() / 60    # time in minutes

        # check for failure and retry
        if self.update_failed:
            if (self.last_update_time_in_minutes + self._failure_delay) < now:
                return self._retrieveJSONObject()
            else:
                return False

        # check for regular update
        if self.needs_update:
            return self._retrieveJSONObject()

        return self.ok

    def _retrieveJSONObject(self):
        """do the actual work and try to retrieve the json object"""
        url = self.url
        if url != '':
            self._last_update_time_in_minutes = time.time() / 60
            self._last_update_time = DateTime()
            
            response = None
            try:
                req = Request(url)
                
                # authenticated if credentials provided
                if self.username and self.password:
                    base64auth = base64.encodestring('%s:%s' %
                        (self.username, self.password))[:-1]
                    req.add_header("Authorization", "Basic %s" % base64auth)
                response = urlopen(req, None, self._request_timeout or None)
            except Exception, e:
                logException(_(u"Error during fetching json data from zimbra "
                               "url: %s" % url), self.context)
            
            if not response:
                self._loaded = True
                self._failed = True
                return False
            
            try:
                data = simplejson.load(response)
            except Exception, e:
                logException(_(u"Error during parsing json data from zimbra "
                               "url: %s" % url), self.context)
                self._loaded = True
                self._failed = True
                return False
            
            self._data = data
            self._loaded = True
            self._failed = False
            
            return True
        
        self._loaded = True
        self._failed = True # no url set means failed
        return False # no url set, but that actually should not really happen

    @property
    def data(self):
        return self._data

class IZimbraMailPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Header"),
        description=_(u"Header of the portlet."),
        required=True,
        default=u'Zimbra Mail')

    protocol = schema.Choice(
        title=_(u'URL Protocol'),
        description=_(u"It's highly recommended to use https:// in case below "
                      "url requires authentification. Otherwise there will be "
                      "chances authentication credentials could be sniffed "
                      "during remote request."),
        required=True,
        default='https://',
        values=('https://', 'http://'))

    url = schema.ASCIILine(
        title=_(u"Zimbra service URL"),
        description=_(u"Root url to your Zimbra service. Please, do not include"
                      " url protocol into the link."),
        required=True,
        default='zcs.vnc.biz')

    folder_id = schema.ASCIILine(
        title=_(u"Mail Folder Id"),
        description=_(u"The name of the mail folder to access. This can be a "
                      "default or a user-defined folder. Default folders "
                      "include: inbox, drafts, sent, trash, junk."),
        required=True,
        default='inbox')

    count = schema.Int(
       title=_(u"Number of items to display"),
       description=_(u"How many items to list."),
       required=True,
       default=5)
    
    username = schema.ASCIILine(
        title=_(u"Username"),
        description=_(u"If not set, zimbra_username property of authenticated "
                      "user will be used."),
        required=False,
        default='')

    password = schema.Password(
        title=_(u"Password"),
        description=_(u"If not set, zimbra_password property of authenticated "
                      "user will be used."),
        required=False,
        default=u'')

    timeout = schema.Int(
        title=_(u"Data reload timeout"),
        description=_(u"Time in minutes after which the data should be reloaded"
                      " from Zimbra service. Minimun value: 1 minute."),
        required=True,
        default=5,
        min=1)

    request_timeout = schema.Int(
        title=_(u"Request timeout"),
        description=_(u"How many seconds to wait for hanging Zimbra request."),
        required=True,
        default=15)
    
    failure_delay = schema.Int(
        title=_(u"Failure delay"),
        description=_(u"Time in minutes before retry to load data from Zimbra "
                      "after a failure"),
        required=True,
        default=5)

class Assignment(base.Assignment):
    implements(IZimbraMailPortlet)

    header = u'Zimbra Mail'
    protocol = 'https://'
    url = 'zcs.vnc.biz'
    folder_id = 'inbox'
    count = 5
    username = ''
    password = u''
    timeout = 5
    request_timeout = 15
    failure_delay = 5

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=u'', protocol='https://', url='zcs.vnc.biz',
                 folder_id='inbox', count=5, username='', password=u'',
                 timeout=5, request_timeout=15, failure_delay=5):
        self.header = header
        self.protocol = protocol
        self.url = url
        self.folder_id = folder_id
        self.count = count
        self.username = username
        self.password = password
        self.timeout = timeout
        self.request_timeout = request_timeout
        self.failure_delay = failure_delay

class Renderer(base.DeferredRenderer):

    render_full = ZopeTwoPageTemplateFile('templates/zimbra_mail.pt')

    @property
    def initializing(self):
        """Should return True if deferred template should be displayed"""
        json = self._getJSON()
        if not json.loaded:
            return True
        if json.needs_update:
            return True
        return False

    def deferred_update(self):
        """Refresh data for serving via KSS"""
        json = self._getJSON()
        json.update()

    def update(self):
        """Update data before rendering. We can not wait for KSS since users
        may not be using KSS."""
        self.deferred_update()

    def _getJSON(self):
        """return a feed object but do not update it"""
        url = self.url
        json = JSON_DATA.get(url, None)
        username, password = self.getAuthCredentials()
        
        # remove json from cache in case password or timeout were changed
        # username, url and folder id are already included into url so
        # their update will automatically expire cached json object
        if json is not None:
            if password != json.password or self.data.timeout != json._timeout:
                json = None
        
        if json is None:
            # create it
            json = JSON_DATA[url] = \
                JSONObject(self.context, url, self.data.timeout, username,
                    password, self.data.request_timeout,
                    self.data.failure_delay)
        return json

    @memoize
    def getAuthCredentials(self):
        """Returns username and password for zimbra user."""
        username, password = self.data.username, self.data.password
        if not (username and password): 
            # take username and password from authenticated user Zimbra creds
            mtool = getToolByName(self.context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            username, password = member.getProperty('zimbra_username', ''), \
                member.getProperty('zimbra_password', '')
        # password could contain non-ascii chars, ensure it's properly encoded
        return username, safe_unicode(password).encode('utf-8')

    @property
    def url(self):
        """return url of json for portlet"""
        ZIMBRA_MAIL_URL_PAT = '%(url)s/home/%(username)s/%(folder_id)s?fmt=json'
        username, password = self.getAuthCredentials()
        return ZIMBRA_MAIL_URL_PAT % {
            'url': self.data.protocol + self.data.url,
            'username': username,
            'folder_id': self.data.folder_id}

    @property
    def title(self):
        """return title of feed for portlet"""
        return self.data.header

    @property
    def feedAvailable(self):
        """checks if the feed data is available"""
        return self._getJSON().ok

    @property
    def _data(self):
        return self._getJSON().data

    @property
    def items(self):
        """Prepare required data from json to display in our portlet"""
        items = []
        url = safe_unicode(self.data.protocol + self.data.url)
        for item in self._data.get('m', []):
            updated = item.get('d', None)
            if updated:
                try:
                    updated = datetime.fromtimestamp(int(updated)/1000.0)
                except Exception, e:
                    pass
            items.append({
                'url': url,
                'title': safe_unicode(item.get('su', '')),
                'updated': updated,
                'body': safe_unicode(item.get('fr', ''))})
        
        items.reverse()
        
        return items[:self.data.count]

    @property
    def enabled(self):
        return self._getJSON().ok

class AddForm(base.AddForm):
    form_fields = form.Fields(IZimbraMailPortlet)
    label = _(u"Add Zimbra Mail Portlet")
    description = _(u"This portlet displays an Zimbra Mail entries.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IZimbraMailPortlet)
    label = _(u"Edit Zimbra Mail Portlet")
    description = _(u"This portlet displays an Zimbra Mail entries.")
