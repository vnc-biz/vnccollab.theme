"""Miscellaneous utility functions"""

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
