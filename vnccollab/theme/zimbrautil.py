from pyzimbra.z.client import ZimbraClient

from zope.interface import implements, Interface
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode as su
from plone.memoize.instance import memoize


class IZimbraUtil(Interface):
    """Interface for Zimbra Utility"""

    def get_client(url_or_context, username='', password=''):
        """Returns an authenticated zimbra client.

        If no username is given, it's used the current user information.
        """


VNC_ZIMBRA_URL = 'https://zcs.vnc.biz'


class ZimbraUtil:
    """Zimbra Utility."""
    implements(IZimbraUtil)


    @memoize
    def get_client(self, url=VNC_ZIMBRA_URL, username='', password=''):
        '''Returns a ZimbraUserClient.

        Args:
          @url - URL of the zimbra server, withou '/service/soap'
          @username - Login of the user. If not present, the client
                      won't be authenticated.
          @password - Password of the user.
        '''
        url = url + '/service/soap'
        client = ZimbraUtilClient(url, username, password)
        return client


class ZimbraUtilClient:
    '''
    Zimbra client support class.

    It returns ZimbraClient results in a way more digerible by plone.
    '''
    def __init__(self, url, username='', password=''):
        self.url = url
        self.client = ZimbraClient(url)
        if username:
            self.authenticate(username, password)

    def authenticate(self, username, password):
        self.client.authenticate(username, password)

    def get_emails(self, folder=None, offset=0, limit=10,
                  recip='1', sortBy='dateDesc'):
        """Returns list of email conversations.

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

        return [self._dict_from_mail(x) for x in result]

    def get_email(self, eid):
        """Returns email by given id.

        It also marks conversation as read.
        """
        result = self.client.invoke('urn:zimbraMail', 'GetConvRequest',
            {'c': {'id': eid, 'fetch': 'all', 'html': '1'}}).m

        # TODO: make zimbra conversation as read
        if not isinstance(result, list):
            result = [result]

        return result

    def get_email_thread(self, eid):
        """Returns conversation emails by given id.

        It also marks conversation as read.
        """
        result = self.get_email(eid)

        thread = []
        for item in result:
            from_ = [su(e._getAttr('p')) for e in item.e
                        if e._getAttr('t') == 'f']
            from_ = from_[0] if len(from_) else ''
            to =  u', '.join([su(e._getAttr('d')) for e in item.e
                        if e._getAttr('t') == 't'])

            thread.append({
                'from': from_,
                'to': to,
                'body': item,
                'id': item._getAttr('_orig_id'),
                'date': item._getAttr('d'),
            })

            return thread

    def _dict_from_mail(self, mail):
        """Converts a zimbra mail into a dictionary"""
        people = mail.e
        if not isinstance(people, list):
            people = [people]

        dct = {
            'subject': su(mail.su),
            'body': u'%s (%s) - %s - %s' % (u', '.join([p._getAttr('d')
                    for p in people]), mail._getAttr('n'), su(mail.su),
                    su(mail.fr)),
            'unread': u'u' in (mail._getAttr('f') or ''),
            'id': mail._getAttr('_orig_id'),
            'date': mail._getAttr('d'),
        }
        return dct

    def create_task(self, dct):
        """Creates a task, given its description as a dictionary"""
        task = dict(**dct)
        task['startDate'] = self._stringFromDate(task['startDate'])
        task['endDate'] = self._stringFromDate(task['endDate'])

        query = {
            'm': {
              #'l' : '24486', # List id. It could be ommited
              'inv' : {
                'comp' : {
                  'name' : task.get('subject', ''),
                  'loc'  : task.get('location', ''),
                  'percentComplete' : task.get('percentComplete', '0'),
                  'status' : task.get('status', 'NEED'),    # Not started
                  'priority' : task.get('priority', '5'),   # Normal
                  's' : {'d' : task.get('startDate', '')},
                  'e' : {'d' : task.get('endDate', '')},
                  'or' : {'a' : task['author'],             # Required
                        'd' : task.get('authorName', ''),
                  },
                },
              },
              'mp' : {
                'ct' : 'text/plain',
                'content' : task.get('content', '')
              },
            }
        }

        result = self.client.invoke('urn:zimbraMail', 'CreateTaskRequest', query)
        return result

    def _stringFromDate(self, date=None):
        if not date:
            return ''
        return date.strftime('%Y%m%d')


zimbraUtilInstance = ZimbraUtil()
