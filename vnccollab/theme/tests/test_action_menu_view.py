from Products.CMFCore.utils import getToolByName
from vnccollab.theme.tests.base import FunctionalTestCase


class TestActionMenuView(FunctionalTestCase):
    def test_languages(self):
        browser = self.login()

        browser.open(self.portal_url)
        self.assertNotIn('portal-languageselector', browser.contents)
        self.assertIn('personaltools-languageselector', browser.contents)

        #print browser.contents
        # tool = getToolByName(self.portal, 'portal_languages', None)
        # defaultLanguage = 'en'
        # supportedLanguages = ['en', 'de', 'no']
        # if tool is not None:
        #     tool.manage_setLanguageSettings(defaultLanguage,
        #                                     supportedLanguages,
        #                                     setUseCombinedLanguageCodes=False)
        # print "\n", " ------- " * 10
        # print tool
        # print tool.getAvailableLanguageInformation()
        # print tool.getLanguageBindings()
        # print tool.showSelector()
        # print " ------- " * 10
        # browser.open(self.portal_url)
        # print " ------- " * 10
