from urlparse import urlparse
import tldextract

from Acquisition import aq_inner
from zope.component import getUtility

from plone.app.users.browser.account import AccountPanelForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

#from jarn.xmpp.core.interfaces import INodeEscaper
#from jarn.xmpp.core.interfaces import IXMPPPasswordStorage

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

    def domain(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        cnetloc= tldextract.extract(urlparse(portal_url).netloc)
        return '.'.join([c for c in cnetloc[1:] if c])

    def imDetails(self):
#        escaper = getUtility(INodeEscaper)
        storage = getUtility(IXMPPPasswordStorage)
        return [('username', ''),#escaper.escape(self._getMemberId())),
                ('password', storage.get(self._getMemberId())),
                ('domain', self.domain()),
                ('port','5222')]
