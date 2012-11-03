from zope import schema
from zope.component import adapts
from zope.interface import implements, Interface
from zope.publisher.browser import IBrowserRequest

from collective.customizablePersonalizeForm.adapters.interfaces import \
        IExtendedUserDataSchema, IExtendedUserDataPanel

from vnccollab.theme import messageFactory as _


class UserDataSchemaAdapter(object):
    adapts(object, IBrowserRequest)
    implements(IExtendedUserDataSchema)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getSchema(self):
        return IUserDataSchema

class UserDataSchemaPropertiesAdapter(object):
    adapts(object, IBrowserRequest)
    implements(IExtendedUserDataPanel)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getProperties(self):
        return ['zimbra_username', 'zimbra_password',
                'etherpad_url', 'etherpad_username', 'etherpad_password',
                'openerp_username', 'openerp_password',
                'redmine_username', 'redmine_password'
                ]

class IUserDataSchema(Interface):

    zimbra_username = schema.ASCIILine(
        title=_("Zimbra Username"),
        description=_(u"We need this field in order to display your Zimbra "
                      "related information, like mail box, calendar, contacts, "
                      "etc..."),
        required=False)

    zimbra_password = schema.Password(
        title=_("Zimbra Password"),
        description=_(u"We need this field in order to display your Zimbra "
                      "related information, like mail box, calendar, contacts, "
                      "etc..."),
        required=False)

    etherpad_url = schema.URI(
        title=_(u"Etherpad URL"),
        description=_(u"Root url to your Etherpad service. This field is "
            "usually useful in case every user got his own Etherpad url instead"
            " of using one global domain for all users."),
        required=False)

    etherpad_username = schema.ASCIILine(
        title=_("Etherpad Username"),
        description=_(u"We need this field in order to display your Etherpad "
                      "related information, like single pad or whole list of "
                      "pads, etc..."),
        required=False)

    etherpad_password = schema.Password(
        title=_("Etherpad Password"),
        description=_(u"We need this field in order to display your Etherpad "
                      "related information, like single pad or whole list of "
                      "pads, etc..."),
        required=False)

    openerp_username = schema.ASCIILine(
        title=_("OpenERP Username"),
        description=_(u"We need this field in order to display your OpenERP "
                      "related information."),
        required=False)

    openerp_password = schema.Password(
        title=_("OpenERP Password"),
        description=_(u"We need this field in order to display your OpenERP "
                      "related information."),
        required=False)

    redmine_username = schema.ASCIILine(
        title=_("Redmine Username"),
        description=_(u"We need this field in order to display your Redmine "
                      "related information."),
        required=False)

    redmine_password = schema.Password(
        title=_("Redmine Password"),
        description=_(u"We need this field in order to display your Redmine "
                      "related information."),
        required=False)
