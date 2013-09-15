"""Miscellaneous utility functions"""
from math import ceil
from pyzimbra.auth import AuthException

from plone.memoize.instance import memoize
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.navtree import buildFolderTree

from zope.component import getUtility, getMultiAdapter
from zope.annotation.interfaces import IAnnotations

from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName

from Acquisition import aq_inner

from vnccollab.theme.zimbrautil import IZimbraUtil


def getAllActiveResources(klass, limit=100, page=1):
    """Returns all items from ActiveResource class.

    @klass: ActiveResource inherited class
    @limit: amount of items in one page query
    @page: page number to get items from

    Mosty used for Redmine REST API calls to get all items
    using pagination.
    """
    # yiled given page items
    res = klass.find(limit=limit, page=page)
    for item in res:
        yield item

    # check if we got any more pages left
    if len(res) >= limit:
        for item in getAllActiveResources(klass, limit=limit, page=page + 1):
            yield item


def getZimbraUrl(context):
    #TODO: get zimbra url from registry
    return 'https://zcs.vnc.biz'


def getZimbraEmail(context):
    mtool = getToolByName(context, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    email = member.getProperty('email')
    return email


def getZimbraClient(context):
    username, password = getZimbraCredentials(context)

    try:
        client = getUtility(IZimbraUtil).get_client(username=username,
                                                    password=password)
    except AuthException:
        client = None
    return client


def getZimbraCredentials(context):
    mtool = getToolByName(context, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    username = member.getProperty('zimbra_username', '')
    password = member.getProperty('zimbra_password', '')
    # password could contain non-ascii chars, ensure it's properly encoded
    return username, safe_unicode(password).encode('utf-8')


def _zimbraAnnotatedTaskKey(username):
    '''Returns the key for zimbra tasks annotations associated with a username.'''
    return 'vnccollab.theme.related_zimbra_task.{0}'.format(username)


def getZimbraAnnotatedTasks(context, username):
    ''' Returns the zimbra tasks annotated associated with the give username
    or [] if anonymous.'''
    if not username:
        return []

    annotation = IAnnotations(context)
    key = _zimbraAnnotatedTaskKey(username)
    annotatedTasks = annotation.get(key, [])
    return annotatedTasks


def setZimbraAnnotatedTasks(context, username, tasks):
    '''Sets the zimbra tasks annotated associated with the given username.'''
    if not username:
        return

    annotation = IAnnotations(context)
    key = _zimbraAnnotatedTaskKey(username)
    annotation[key] = tasks


def getZimbraLiveAnnotatedTasks(context):
    ''' Returns the zimbra tasks annotated associated with the authenticated
    user or [] if anonymous.

    If some of the annotated tasks don't exists in the zimbra server, the
    annotation is updated.
    '''
    username, password = getZimbraCredentials(context)
    annotated_tasks = getZimbraAnnotatedTasks(context, username)
    if not annotated_tasks:
        return []

    try:
        # Clean the orphan tasks, the ones are annotated,
        # but don't exist anymore.
        zimbra_util = getUtility(IZimbraUtil)
        zimbra_client = zimbra_util.get_client(username=username,
                                               password=password)
        all_tasks = zimbra_client.get_all_tasks()
        tasks = [x for x in all_tasks if x in annotated_tasks]
        if tasks != annotated_tasks:
            setZimbraAnnotatedTasks(context, username, tasks)
    except:
        # If we can't get all the task, we won't clean the orphans.
        tasks = annotated_tasks
    return tasks


def addZimbraAnnotatedTasks(context, task):
    '''Adds a task to the zimbra annotated tasks of the context.'''
    username, _ = getZimbraCredentials(context)
    annotatedTasks = getZimbraAnnotatedTasks(context, username)
    annotatedTasks.append(task)
    setZimbraAnnotatedTasks(context, username, annotatedTasks)


def groupList(value, batch_size=None, groups_number=None):
    """Divide give list into groups"""
    if not value:
        return ()

    value = value[:]

    # we can group by group size or by groups number
    if groups_number is not None:
        size = int(ceil(len(value) / float(groups_number)))
    else:
        size = batch_size

    assert size is not None

    # add zeros to get even number of elems for size
    # to preform further grouping
    if len(value) % size != 0:
        value.extend([0 for i in range(size - len(value) % size)])

    # group elements into batches
    value = zip(*[value[i::size] for i in range(size)])

    # finally filter out any zeros we added before grouping
    value[-1] = tuple([k for k in value[-1] if k != 0])

    return value


def sortNavTree(tree):
    result = sorted(tree, key=lambda e: e['Title'])
    for element in result:
        if 'children' in element:
            element['children'] = sortNavTree(element['children'])
    return result


@memoize
def getNavTree(self, _marker=[]):
    u""" Pathed method from plone.app.portlets.portlets.navigation.Renderer
         Sorting result alphabetically.
    """
    context = aq_inner(self.context)
    queryBuilder = getMultiAdapter(
        (context, self.data), INavigationQueryBuilder)
    strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

    result = buildFolderTree(
        context, obj=context, query=queryBuilder(), strategy=strategy)

    if 'children' in result:
        result['children'] = sortNavTree(result['children'])

    return result


def sendto(self, send_to_address, send_from_address, comment,
           subject='Plone', **kwargs):
    """Pathed method from Products.CMFPlone.PloneTool.PloneTool.
       Sends a link of a page to someone."""
    host = self.getMailHost()
    template = getattr(self, 'sendto_template')
    portal = getToolByName(self, 'portal_url').getPortalObject()
    encoding = portal.getProperty('email_charset')
    if 'envelope_from' in kwargs:
        envelope_from = kwargs['envelope_from']
    else:
        envelope_from = send_from_address
    # Cook from template
    message = template(self, send_to_address=send_to_address,
                       send_from_address=send_from_address,
                       comment=comment, subject=subject, **kwargs)
    message = message.encode(encoding)
    host.send(message, mto=send_to_address,
              mfrom=envelope_from, subject=subject,
              charset=self.getSiteEncoding(), msg_type='text/html')
