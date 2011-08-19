import json
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from cioppino.twothumbs import _
from cioppino.twothumbs import rate

class LikeThisShizzleView(BrowserView):
    """ Update the like/unlike status of a product via AJAX """

    def __call__(self, REQUEST, RESPONSE):
        form = self.request.form
        if form.get('form.lovinit', False):
            rate.loveIt(self.context)
            # vipod: additionally re-index a few more indexes
            self.context.reindexObject(idxs=['avg_ratings',
                'total_down_ratings'])
        elif form.get('form.hatedit', False):
            rate.hateIt(self.context)
            # vipod: additionally re-index a few more indexes
            self.context.reindexObject(idxs=['avg_ratings',
                'total_down_ratings'])
        else:
            return _(u"We don't like ambiguity around here. "
                     "Check yo self before you wreck yo self.")

        tally = rate.getTally(self.context)
        RESPONSE.setHeader('Content-Type', 'application/javascript')
        return json.dumps(tally)
