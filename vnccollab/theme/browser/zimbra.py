import simplejson

from pyzimbra.z.client import ZimbraClient

from Acquisition import aq_inner
from AccessControl import getSecurityManager

from Products.Five.browser import BrowserView

from plone.memoize.instance import memoize
from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key

from vnccollab.theme import messageFactory as _


class ZimbraMailPortletView(BrowserView):
    """High level Zimbra Mail Portlet view to communicate with Zimbra SOAP API.
    
    It uses pyzimbra and SOAPpy.
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def view_name(self):
        """To refer to itself in a bit more generic way"""
        return self.__name__

    def __call__(self, action, portlethash):
        """Main method that accepts action to perform.
        
        Args:
          @action - one of allowed actions, like emails, create, send, etc...
          @portlethash - portlet hash so we get portlet assignement data from it
        
        This method accepts only post requests.
        It returns json.
        It authenticates before any further actions.
        """
        request = self.request
        
        # check if method is POST
        if self.request.method != 'POST':
            return self._error(_(u"Request method is not allowed."))
        
        # check if action is valid
        if action not in ('emails',):
            return self._error(_(u"Requested action is not allowed."))
        
        # get settings
        data = self._data()
        
        # create zimbra client and authenticate
        self.client = ZimbraClient('%s/service/soap' % data['url'])
        self._authenticate()

        # perform actual action
        if action == 'emails':
            return self.get_emails(request.get('folder_id'),
                int(request.get('start') or '0'),
                int(request.get('limit') or '0'))
        
        return self._error(_(u"Requested action is not defined"))

    def _error(self, msg):
        return simplejson.dump({'error': msg})

    def _authenticate(self):
        """Authenticated to Zimbra SOAP"""
        data = self._data()
        self.client.authenticate(data['username'], data['password'])
    
    def get_emails(self, folder=None, start=0, limit=10):
        """Returns list of emails.
        
        Args:
          @folder - if given, return list of emails from inside this folder
          @start - if given, return list of emails starting from start
          @limit - return 'limit' number of emails
        """
        # TODO: use start argument
        result = self.client.invoke('urn:zimbraMail', 'SearchRequest',
            {'types': 'message', 'limit': limit, 'fetch':'none'})
        return ()

    def create_email(self):
        return None

    @memoize
    def _data(self, portlethash):
        """Returns zimbra mail related settings based on portlet assignment
        object and currently logged in user.
        """
        context = aq_inner(self.context)
        info = unhashPortletInfo(portlethash)
        assignment = assignment_mapping_from_key(context, info['manager'],                                                                       
            info['category'], info['key'])[info['name']]
        renderer = Renderer(context, self.request, self, None, sassignment)
        username, password = renderer.getAuthCredentials()
        return {
            'url': assignment.url,
            'folder_id': assignment.folder_id,
            'emails_limit': assignment.count,
            'username': username,
            'password': password
        }
