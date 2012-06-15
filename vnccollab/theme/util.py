"""Miscellaneous utility functions"""
from math import ceil

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

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
        for item in getAllActiveResources(klass, limit=limit, page=page+1):
            yield item

def getZimbraUrl(context):
    #TODO: get zimbra url from registry
    return 'https://zcs.vnc.biz'

def getZimbraEmail(context):
    mtool = getToolByName(context, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    email = member.getProperty('email')
    return email

def getZimbraCredentials(context):
    mtool = getToolByName(context, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    username = member.getProperty('zimbra_username', '')
    password = member.getProperty('zimbra_password', '')
    # password could contain non-ascii chars, ensure it's properly encoded
    return username, safe_unicode(password).encode('utf-8')

def groupList(value, batch_size=None, groups_number=None):
    """Divide give list into groups"""
    if not value:
        return ()

    value = value[:]
    
    # we can group by group size or by groups number
    if groups_number is not None:
        size = int(ceil(len(value)/float(groups_number)))
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
