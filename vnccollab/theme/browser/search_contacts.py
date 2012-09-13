import json

from Acquisition import aq_inner

from zope.component import getMultiAdapter

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class SearchContacts(BrowserView):

    def __call__(self):
        searchtext = self.request.form.get('q')
        if len(searchtext) < 3:
            return []

        search_view = getMultiAdapter((aq_inner(self.context), self.request),
                        name='usergroup-userprefs')

        mtool = getToolByName(self.context, 'portal_membership')
        myself_id = mtool.getAuthenticatedMember().getId()
        results = search_view.membershipSearch(searchString=searchtext,
                                               searchGroups=False,
                                               ignore=[myself_id])
        data = []
        for m in results:
            if m:
                data.append({'fullname': m.getProperty('fullname'),
                             'id': m.getId()})
        
        return json.dumps(data)
