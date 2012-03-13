import xmlrpclib

from zope.formlib import form
from zope.interface import implements, Interface
from zope.component import getUtility
from zope import schema

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from vnccollab.theme import messageFactory as _


class IOpenERPJSPortlet(IPortletDataProvider):
    header = schema.TextLine(
        title=_(u"Header"),
        description=_(u"Header of the portlet."),
        required=True,
        default=u'OpenERP JavaScript Portlet')

    url = schema.URI(
        title=_(u"OpenERP URL"),
        description=_(u"Root url to your OpenERP service."),
        required=True,
        default='http://demo.vnc.biz:8085')

    dbname = schema.TextLine(
        title=_(u"Database Name"),
        description=_(u"Name of the database of your OpenERP service."),
        required=True,
        default=u'openerp_v61_demo')

    action_id = schema.Int(
        title=_(u"action_id"),
        description=_(u"Code of the OpenERP action_id to execute."),
        required=True,
        default=617)

    embedded_url = schema.URI(
        title=_(u"Embedded URL"),
        description=_(u"You can put here the embedded URL of the OpenERP widget, if you have it."),
        required=False)


class Assignment(base.Assignment):
    implements(IOpenERPJSPortlet)

    header = u'OpenERP Customers'
    url = u'http://demo.vnc.biz:8085'
    dbname  = u'openerp_v61_demo'
    action_id = 617
    embedded_url = None

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=header, url=url, dbname=dbname,
                 action_id=action_id, embedded_url=embedded_url):
        self.header = header
        self.url = url
        self.dbname = dbname
        self.action_id = action_id
        self.embedded_url = ''
        self._initEmbeddedURL()

    def _getAuthCredentials(self):
        """Returns username and password for zimbra user."""
        # TODO: this is a copy of zimbra_mail.Renderer.getAuthCredentials,
        # it should be factored out in the future.
        username, password = self.data.username, self.data.password
        if not (username and password):
            # take username and password from authenticated user Zimbra creds
            mtool = getToolByName(self.context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            username, password = member.getProperty('zimbra_username', ''), \
                member.getProperty('zimbra_password', '')
        # password could contain non-ascii chars, ensure it's properly encoded
        return username, safe_unicode(password).encode('utf-8')

    def _auth(self):
        '''Get OpenERP embed 'uid' from user id and password'''
        server = xmlrpclib.ServerProxy(self.url + '/xmlrpc/common')
        login, pwd = self._getAuthCredentials()
        uid = server.login(self.dbname, login, pwd)
        return uid, pwd

    def _initEmbeddedURL(self):
        if self.embedded_url:
            return

        model = 'share.wizard'
        uid, pwd = self._auth()
        args = [self.action_id]

        server = xmlrpclib.ServerProxy(self.url + '/xmlrpc/object')
        server.execute(self.dbname, uid, pwd, model, 'go_step_1', args)
        server.execute(self.dbname, uid, pwd, model, 'go_step_2', args)
        r = server.execute(self.dbname, uid, pwd, model, 'export_data', ['embed_url'])
        self.embedded_url = r['datas'][0][0]


class Renderer(base.Renderer):

    render = ZopeTwoPageTemplateFile('templates/openerp_js.pt')

    @property
    def title(self):
        """return title of feed for portlet"""
        return self.data.header


class AddForm(base.AddForm):
    form_fields = form.Fields(IOpenERPJSPortlet)
    label = _(u"Add OpenERP JavaScript Portlet")
    description = _(u"Create an OpenERP JavaScript Portlet.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IOpenERPJSPortlet)
    label = _(u"Edit OpenERP JavaScript Portlet")
    description = _(u"This portlet allows managing the OpenERP JavaScript Portlet.")


