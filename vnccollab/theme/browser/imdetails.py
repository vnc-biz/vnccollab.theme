from Acquisition import aq_inner
from zope.component import getUtility

from plone.app.users.browser.account import AccountPanelForm
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from jarn.xmpp.core.interfaces import INodeEscaper
from jarn.xmpp.core.interfaces import IXMPPPasswordStorage

class IMDetailsPanel(AccountPanelForm):
    """ Implementation of 'IM Details' page."""

    template = ViewPageTemplateFile('templates/imdetails.pt')

    def getIMDetailsLink(self):
        context = aq_inner(self.context)

        template = None
        if self._checkPermission('Set own properties', context):
            template = '@@im-details'

        return template

    def _getMemberId(self):
        mt = getToolByName(self.context, 'portal_membership')
        member = mt.getAuthenticatedMember()
        return member.getMemberId()

    def imDetails(self):
        escaper = getUtility(INodeEscaper)
        storage = getUtility(IXMPPPasswordStorage)
        registry = getUtility(IRegistry)
        return [('username', escaper.escape(self._getMemberId())),
                ('password', storage.get(self._getMemberId())),
                ('domain', registry.get('jarn.xmpp.xmppDomain', '')),
                ('port','5222')]
