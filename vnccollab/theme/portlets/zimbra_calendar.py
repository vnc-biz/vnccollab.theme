from zope import schema
from zope.formlib import form
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from vnccollab.theme import messageFactory as _


class IZimbraCalendarPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Header"),
        description=_(u"Header of the portlet."),
        required=True,
        default=u'Zimbra Calendar')

    url = schema.URI(
        title=_(u"Zimbra service URL"),
        description=_(u"Root url to your Zimbra service."),
        required=True,
        default='https://')

    mail_domain = schema.TextLine(
        title=_(u"Domain of the mail account"),
        description=_(u"The part after the '@'."),
        required=True,
        default=u'vnc.biz')

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

    calendar_name = schema.TextLine(
        title=_(u"Name of The Calendar"),
        description=_(u"Which calendar should be displayed."),
        required=True,
        default=u'Calendar')

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
    implements(IZimbraCalendarPortlet)

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=u'', url=u'https://',
                 mail_domain=u'vnc.biz',
                 username=u'', password=u'', calendar_name=u'',
                 timeout=5, request_timeout=15, failure_delay=5):
        self.header = header
        self.url = url
        self.mail_domain = mail_domain
        self.username = username
        self.password = password
        self.calendar_name = calendar_name
        self.timeout = timeout
        self.request_timeout = request_timeout
        self.failure_delay = failure_delay


class AddForm(base.AddForm):
    form_fields = form.Fields(IZimbraCalendarPortlet)
    label = _(u"Add Zimbra Calendar Portlet")
    description = _(u"This portlet allows managing Zimbra Calendar.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IZimbraCalendarPortlet)
    label = _(u"Edit Zimbra Calendar Portlet")
    description = _(u"This portlet allows managing Zimbra Calendar.")


class Renderer(base.Renderer):

    render = ZopeTwoPageTemplateFile('templates/zimbra_calendar.pt')

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
    def title(self):
        """return title of feed for portlet"""
        return self.data.header

    @property
    def src(self):
        '''Returs the url of the zimbra calendar'''
        username, password = self.getAuthCredentials()
        src = '%s/service/home/%s@%s/%s.html' % (
               self.data.url, username, self.data.mail_domain,
               self.data.calendar_name)
        return src
