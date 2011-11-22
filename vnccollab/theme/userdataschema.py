from zope import schema
from zope.interface import implements

from plone.app.users import userdataschema as base

from vnccollab.theme import messageFactory as _


class UserDataSchemaProvider(object):
    implements(base.IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IUserDataSchema

class IUserDataSchema(base.IUserDataSchema):

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
