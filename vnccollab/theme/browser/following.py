import json

from AccessControl import getSecurityManager

from zope.component import getUtility

from Products.Five.browser import BrowserView

from ..interfaces import IFollowing


class FollowingView(BrowserView):
    """Provides utility functions for templates regarding users following
    functionality.
    """

    def follow_user(self, user1, user2):
        """Subscribe user1 to user2.

        If user1 is None, get authenticated user id.
        """
        user = user1 and user1 or getSecurityManager().getUser().getId()
        following = getUtility(IFollowing)
        following.subscribe(user, user2)

        self.request.response.setHeader('Content-Type',
            'application/javascript')                                                                       
        return json.dumps({
            'title': 'Unfollow',
            'label': 'Following',
            'following': True,
        })

    def unfollow_user(self, user1, user2):
        """UnSubscribe user1 from user2.

        If user1 is None, get authenticated user id.
        """
        user = user1 and user1 or getSecurityManager().getUser().getId()
        following = getUtility(IFollowing)
        following.unsubscribe(user, user2)

        self.request.response.setHeader('Content-Type',
            'application/javascript')                                                                       
        return json.dumps({
            'title': 'Follow',
            'label': 'Follow',
            'following': False,
        })

    def follow_button(self, user1, user2):
        """Returns following button details depending on subscription settings.
        user1 - profile owner, owner of follow button
        user2 - user that wants to see follow button for user1

        If no userid given, get authenticated user id.
        """
        user = user2 and user2 or getSecurityManager().getUser().getId()

        # return nothing if users are equal
        if user == user1:
            return {}

        # check if user1 is followed by user
        button = {}
        following = getUtility(IFollowing)
        if following.is_following(user, user1):
            button = {
                'title': 'Unfollow',
                'label': 'Following',
                'following': True,
            }
        else:
            button = {
                'title': 'Follow',
                'label': 'Follow',
                'following': False,
            }

        return button
