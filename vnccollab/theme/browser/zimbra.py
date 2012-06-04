import types
import simplejson

from pyzimbra.z.client import ZimbraClient

from Acquisition import aq_inner
from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFPlone.utils import safe_unicode as su

from plone.memoize.instance import memoize
from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key

from vnccollab.theme.portlets.zimbra_mail import Renderer
from vnccollab.theme import messageFactory as _


def findMsgBody(node, format='text/html'):
    """Recursively goes over attachments and finds body"""
    if hasattr(node, '_name') and node._name == 'mp' and \
       hasattr(node, '_getAttr') and node._getAttr('body') == '1' and \
       node._getAttr('ct') == format and hasattr(node, 'content'):
        return su(node.content)

    if hasattr(node, 'mp'):
        mp = node.mp
        if not isinstance(mp, (types.ListType, types.TupleType)):
            mp = [mp]
        for sub_node in mp:
            body = findMsgBody(sub_node, format)
            if body:
                return body

    return u''


class ZimbraMailPortletView(BrowserView):
    """High level Zimbra Mail Portlet view to communicate with Zimbra SOAP API.

    It uses pyzimbra and SOAPpy.
    """

    _emails_template = ZopeTwoPageTemplateFile(
        'templates/zimbra_emails_template.pt')

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
        # get settings
        data = self._data(portlethash)

        # check if method is POST
        request = self.request
        if request.method != 'POST':
            return self._error(_(u"Request method is not allowed."))

        # check if action is valid
        if action not in ('emails', 'email'):
            return self._error(_(u"Requested action is not allowed."))

        mails = self._execute_action(action, data, request)
        return simplejson.dumps(mails)

    def _execute_action(self, action, data, request={}):
        # create zimbra client and authenticate
        self.data = data
        self.client = ZimbraClient('%s/service/soap' % data['url'])
        self._authenticate()

        # perform actual action
        mails = []
        if action == 'emails':
            mails = self.get_emails(request.get('folder') or None,
                int(request.get('offset') or '0'),
                int(request.get('limit') or '100'),
                request.get('recip') or '1',
                request.get('sortBy') or 'dateDesc'
            )
        elif action == 'emails_as_dicts':
            mails = self.get_emails_as_dicts(request.get('folder') or None,
                int(request.get('offset') or '0'),
                int(request.get('limit') or '100'),
                request.get('recip') or '1',
                request.get('sortBy') or 'dateDesc'
            )
        elif action == 'email':
            mails = self.get_email(request.get('eid') or None)

        return mails

    def _error(self, msg):
        return simplejson.dumps({'error': msg})

    def _authenticate(self):
        """Authenticated to Zimbra SOAP"""
        # TODO: do not login every request, but only on timing bases (e.g.
        #       every 10 minutes)
        self.client.authenticate(self.data['username'], self.data['password'])

    def get_emails_as_dicts(self, folder=None, offset=0, limit=10, recip='1',
                   sortBy='dateDesc'):
        """Returns list of email conversations. Each email is represented by a dict.

        Args:
          @folder - if given, return list of emails from inside this folder
          @offset - if given, return list of emails starting from start
          @limit - return 'limit' number of emails
          @recip - whether to return 'to' email adress instead of 'from' for
                   sent messages and conversations
          @sort_by - sort result set by given field
        """
        query = {
            'types': 'conversation',
            'limit': limit,
            'offset': offset,
            'recip': recip,
            'sortBy': sortBy,
        }
        if folder:
            query['query'] = 'in:%s' % folder
        result = self.client.invoke('urn:zimbraMail', 'SearchRequest', query)

        # if result contains only one item then it won't be list
        if not isinstance(result, list):
            result = [result]

        emails = []
        for item in result:
            # prepare senders list
            people = item.e
            if not isinstance(people, list):
                people = [people]

            emails.append({
                'subject': su(item.su),
                'body': u'%s (%s) - %s - %s' % (u', '.join([p._getAttr('d')
                    for p in people]), item._getAttr('n'), su(item.su),
                    su(item.fr)),
                'unread': u'u' in (item._getAttr('f') or ''),
                'id': item._getAttr('_orig_id'),
                'date': item._getAttr('d'),
            })

        return emails

    def get_emails(self, folder=None, offset=0, limit=10, recip='1',
                   sortBy='dateDesc'):
        """Returns list of email conversations.

        Args:
          @folder - if given, return list of emails from inside this folder
          @offset - if given, return list of emails starting from start
          @limit - return 'limit' number of emails
          @recip - whether to return 'to' email adress instead of 'from' for
                   sent messages and conversations
          @sort_by - sort result set by given field
        """

        emails = self.get_emails_as_dicts(folder, offset, limit, recip, sortBy)
        return {'emails': self._emails_template(emails=emails).encode('utf-8')}

    def get_email(self, eid):
        """Returns conversation emails by given id.

        It also marks conversation as read.
        """
        if not eid:
            return {'error': _(u"Conversation id is not valid.")}

        # TODO: make zimbra conversation as read

        result = self.client.invoke('urn:zimbraMail', 'GetConvRequest',
            {'c': {'id': eid, 'fetch': 'all', 'html': '1'}}).m

        # if result contains only one item then it won't be list
        if not isinstance(result, list):
            result = [result]

        thread = []
        for item in result:
            thread.append({
                'from': [su(e._getAttr('p')) for e in item.e
                    if e._getAttr('t') == 'f'][0],
                'to': u', '.join([su(e._getAttr('d')) for e in item.e
                    if e._getAttr('t') == 't']),
                'body': findMsgBody(item),
                'id': item._getAttr('_orig_id'),
                'date': item._getAttr('d'),
            })

        return {'conversation': '<br />'.join([t['from']+': '+t['body']
            for t in thread])}

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
        renderer = Renderer(context, self.request, self, None, assignment)
        username, password = renderer.getAuthCredentials()
        return {
            'url': assignment.url,
            'folder_id': assignment.folder_id,
            'emails_limit': assignment.count,
            'username': username,
            'password': password
        }
