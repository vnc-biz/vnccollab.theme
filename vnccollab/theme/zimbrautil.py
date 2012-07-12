import urlparse
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
        p = urlparse.urlparse(self.url)
        self.server_url = '{0}://{1}'.format(p.scheme, p.netloc)
        self.client = ZimbraClient(url)

        if username:
            self.authenticate(username, password)

    def authenticate(self, username, password):
        self.client.authenticate(username, password)

    def get_emails(self, folder=None, offset=0, limit=10,
                  recip='1', sortBy='dateDesc', types='conversation'):
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
            'types': types,
            'limit': limit,
            'offset': offset,
            'recip': recip,
            'sortBy': sortBy,
        }
        if folder:
            query['query'] = 'in:%s' % folder
        result = self.client.invoke('urn:zimbraMail', 'SearchRequest', query)
        # if we have activated returnAllAttrs, result is a tuple.
        # We're interested here only in its first element
        if type(result) == tuple:
            result = result[0]

        # if result contains only one item then it won't be list
        if not isinstance(result, list):
            result = [result]

        return [self._dict_from_mail(x) for x in result]

    def get_email(self, eid):
        """Returns email by given id.

        It also marks conversation as read.
        """
        result = self.client.invoke('urn:zimbraMail', 'GetConvRequest',
            {'c': {'id': eid, 'fetch': 'all', 'html': '1'}})[0].m

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
        if not people:
            people = []
        elif not isinstance(people, list):
            people = [people]

        dct = {
            'subject': su(mail.su),
            'body': u'%s (%s) - %s - %s' % (u', '.join([p._getAttr('d')
                    for p in people]), mail._getAttr('n'), su(mail.su),
                    su(mail.fr)),
            'unread': u'u' in (mail._getAttr('f') or ''),
            'id': mail._getAttr('_orig_id'),
            'date': mail._getAttr('d'),
            'cid': mail._getAttr('cid'),
        }
        return dct

    def create_task(self, dct):
        """Creates a task, given its description as a dictionary"""
        task = dict(**dct)
        for k,v in task.items():
            if v is None:
                task[k] = u''
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
                  'or' : {'a' : task['author'],             # Required
                        'd' : task.get('authorName', ''),
                  },
                },
              },
            }
        }
        if task['content']:
            query['m']['mp'] = {'ct': 'text/plain',
                                'content' : task['content']}
        if task['startDate']:
            query['m']['inv']['comp']['s'] = {'d': task['startDate']}
        if task['endDate']:
            query['m']['inv']['comp']['e'] = {'d': task['endDate']}

        response, _ = self.client.invoke('urn:zimbraMail',
                'CreateTaskRequest', query)
        response = self.get_message(response._getAttr(u'invId'))
        task = self._taskFromGetMsgResponse(response)
        return task

    def get_message(self, id):
        '''Returns a message (mail, task, etc), given its id.'''
        query = {"_jsns":"urn:zimbraMail",
                 "m":{'id': id, 'html': 1, 'needExp': 1, 'max':250000}}
        response, attrs = self.client.invoke('urn:zimbraMail',
                'GetMsgRequest', query)
        return response

    def get_all_tasks(self):
        '''Returns all the zimbra tasks of the authenticated user.'''
        query = {'query': 'in:"tasks"', 'types':'task',}
        response, _ = self.client.invoke('urn:zimbraMail',
                'SearchRequest', query)
        if type(response) <> list:
            response = [response]
        return [self._taskFromSearchResponse(x) for x in response]

    def _taskFromGetMsgResponse(self, response):
        '''Returns a ZimbraTask given a zimbra CreateTaskResponse.'''
        id = response._getAttr('_orig_id')
        title = response.inv.comp._getAttr('name')
        body = getattr(response.inv.comp, 'fr', u'')
        return ZimbraTask(id, title, self.server_url, body)

    def _taskFromSearchResponse(self, response):
        '''Returns a ZImbraTask given a zimbra SearchResponse.'''
        id = response._getAttr('invId')
        title = response._getAttr('name')
        body = getattr(response, 'fr', u'')
        return ZimbraTask(id, title, self.server_url, body)

    def _stringFromDate(self, date=None):
        if not date:
            return ''
        return date.strftime('%Y%m%d')


class ZimbraTask:
    def __init__(self, id, title, server_url, body):
        self.id = id
        self.title = title
        self.server_url = server_url
        self.url = ('{0}/zimbra/h/search?su=1&si=0&so=0&sc=4&st=task'
              + '&id={1}&action=edittask').format(self.server_url, id)
        self.body = body

    def __eq__(self, other):
        return (self.id == other.id) and (self.server_url == other.server_url)

    def __repr__(self):
        if len(self.body) < 10:
            body = repr(self.body)
        else:
            body = repr(self.body[:10]+'...')
        return 'ZimbraTask({0}, {1}, {2})'.format(repr(self.id),
                repr(self.title), body)


zimbraUtilInstance = ZimbraUtil()
