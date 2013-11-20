from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.avatar import AvatarUtil


class FakeImg(object):
    width = 1000
    height = 1000


class TestAvatar(FunctionalTestCase):
    def test_avatar(self):
        img = FakeImg()
        obj = AvatarUtil()
        result = obj.style(img, (100, 80))
        self.assertEqual((80, 80, 'padding: 0px 10px 0px 10px; background-color: black;'), result)
