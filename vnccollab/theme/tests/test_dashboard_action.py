
from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import VNCCOLLAB_THEME_INTEGRATION_TESTING


class DashboardActionTest(FunctionalTestCase):

    layer = VNCCOLLAB_THEME_INTEGRATION_TESTING

    EXPECTED_HTML = """<li id="personaltools-dashboard">
            <a href="{0}/dashboard">Dashboard</a>"""

    def test_dashboard_action(self):
        browser = self.login()
        browser.open(self.portal_url)

        expected_html = self.EXPECTED_HTML.format(self.portal_url)
        self.assertIn(expected_html, browser.contents)
