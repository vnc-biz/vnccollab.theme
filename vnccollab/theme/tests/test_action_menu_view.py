from vnccollab.theme.tests.base import FunctionalTestCase


class TestActionMenuView(FunctionalTestCase):
    members = (
        ('secret', 'Scott Tiger', 'scott@tiger.com', ['members'], '2013-09-24'),
        ('secret', 'Johann Sebastian Bach', 'johan@bach.com', ['members'], '2013-09-24'),)

    def test_languages(self):
        browser = self.login()

        browser.open(self.portal_url)
        self.assertNotIn('portal-languageselector', browser.contents)
        self.assertIn('personaltools-languageselector', browser.contents)
