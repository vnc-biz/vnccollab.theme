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

    origin = schema.URI(
        title=_(u"OpenERP URL"),
        description=_(u"Root url to your OpenERP service."),
        required=True,
        default='http://demo.vnc.biz:8085')

    dbname = schema.TextLine(
        title=_(u"Database Name"),
        description=_(u"Name of the database of your OpenERP service."),
        required=True,
        default=u'openerp_v61_demo')

    action = schema.Int(
        title=_(u"Action"),
        description=_(u"Code of the OpenERP action to execute."),
        required=True,
        default=617)

    options = schema.TextLine(
        # We can't use schema.Dict since the values could be from multiple
        # types.
        title=_(u"Action Options"),
        description=_(u"String representing a dictionary with the options for the action."),
        required=True,
        default=u'{"search_view": true}')



class Assignment(base.Assignment):
    implements(IOpenERPJSPortlet)

    header = u'OpenERP Customers'
    origin = u'http://demo.vnc.biz:8085'
    dbname  = u'openerp_v61_demo'
    action = 617
    options = u'{"search_view": true}'

    SCRIPT = '''
    new openerp.init(["web"]).web.embed("%s", "%s", "%s", "%s", %s, %s);
    '''

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=header, origin=origin, dbname=dbname,
                 action=action, options=options):
        self.header = header
        self.origin = origin
        self.dbname = dbname
        self.action = action
        self.options = options
        # TODO: Calculate these fields
        self.login = 'embedded-e9e3c597782a4b41b11bd98167f9e835'
        self.key = 'JPKDgxdXEy'

    def script_content(self):
        return self.SCRIPT % (self.origin, self.dbname, self.login, self.key,
                              self.action, self.options)


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


