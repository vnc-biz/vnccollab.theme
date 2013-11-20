from zope.publisher.browser import TestRequest

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.wsapi import WSAPIView


class TestWSAPIView(FunctionalTestCase):
    def test_post_and_index_object(self):
        view = WSAPIView(self.portal, self.app.REQUEST)
        result = view.post_and_index_object({})
        self.assertTrue(len(result) == 0)

        objs = {'news1': [{'description': 'News One', 'title': 'news1', 'text': '\n<p>Hot off the press!</p>\n', 'id': 'news1'}, 'News Item']}
        result = view.post_and_index_object(objs)
        self.assertIn('/plone/news1', result)