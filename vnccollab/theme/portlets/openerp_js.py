import xmlrpclib
from urlparse import urlparse, parse_qs

from zope.formlib import form
from zope.interface import implements, Interface
from zope.component import getUtility
from zope import schema
from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

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

    action_id = schema.Choice(
        title=_(u"Widget"),
        description=_(u"OpenERP widget to use."),
        source = 'vnccollab.theme.openerp_js.openerp_vocabulary',
        required=True,)


class Assignment(base.Assignment):
    implements(IOpenERPJSPortlet, IAttributeAnnotatable)

    header = u'OpenERP Customers'
    url = u'http://demo.vnc.biz:8085'
    dbname  = u'openerp_v61_demo'
    action_id = 22

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=header, url=url, dbname=dbname,
                 action_id=action_id):
        self.header = header
        self.url = url
        self.dbname = dbname
        self.action_id = action_id


class Renderer(base.Renderer):

    render = ZopeTwoPageTemplateFile('templates/openerp_js.pt')

    def update(self):
        login, pwd = self._getAuthCredentials()
        annotation = IAnnotations(self.data)
        key = 'vnccollab.theme.openerp_js.embedded_url.{0}.{1}'.format(
                self.data.action_id, login)
        self.embedded_url = annotation.get(key, None)

        if not self.embedded_url:
            annotation[key] = self._embedded_url(login, pwd)
            self.embedded_url = annotation.get(key)

        parsed = urlparse(self.embedded_url)
        dct = parse_qs(parsed.query)

        self.url = '{0}://{1}'.format(parsed.scheme, parsed.netloc)
        self.login = dct['login'][0]
        self.dbname = dct['db'][0]
        self.key= dct['key'][0]
        self.action_id = self.data.action_id


    @property
    def title(self):
        """return title of feed for portlet"""
        return self.data.header

    @memoize
    def _getAuthCredentials(self):
        """Returns username and password for zimbra user."""
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        username, password = member.getProperty('openerp_username', ''), \
            member.getProperty('openerp_password', '')
        # password could contain non-ascii chars, ensure it's properly encoded
        return username, safe_unicode(password).encode('utf-8')

    def _embedded_url(self, login, pwd):
        """Generate the ebedded url for the OpenERP widget associated with the
        current user"""
        url = self.data.url
        dbname = self.data.dbname
        model = 'share.wizard'
        action_id = self.data.action_id
        create_args = { 'name' : '{0}-{1}'.format(login, action_id),
                        'action_id' : action_id}

        server = xmlrpclib.ServerProxy(url + '/xmlrpc/common', allow_none=True)
        uid = server.login(dbname, login, pwd)
        server = xmlrpclib.ServerProxy(url + '/xmlrpc/object', allow_none=True)

        id = server.execute(dbname, uid, pwd, model, 'create', create_args)
        args = [id]
        server.execute(dbname, uid, pwd, model, 'go_step_1', args)
        server.execute(dbname, uid, pwd, model, 'go_step_2', args, {})
        r = server.execute(dbname, uid, pwd, model, 'export_data', args,
                           ['embed_url'])
        embedded_url = r['datas'][0][0]
        return embedded_url


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



'''
How to get the action_id of a widget?

Just visit http://demo.vnc.biz:8085. Go to the page you want to embed, click the green icon in the upper left side of screen, the one with "Link or Embed..." as tooltip and follow the wizard. It will generate a url with an action_id parameter.
'''
OPENERP_VOCAB = [
        #(59,  _(u'Sales - Leads')),
        (150, _(u'Sales - Opportunities')),
        #(562, _(u'Sales - Contracts')),
        (60,  _(u'Sales - Customers')),
        (57,  _(u'Sales - Contacts')),
        (180, _(u'Sales - Products by Category')),
        (178, _(u'Sales - Products')),
]

class OpenERPJSPortletVocabulary():
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(value, title, title) for (value, title) in OPENERP_VOCAB]
        return SimpleVocabulary(items)

openerp_vocabulary = OpenERPJSPortletVocabulary()
