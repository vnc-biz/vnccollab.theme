from zope.interface import alsoProvides
from zope.component import queryMultiAdapter, getSiteManager
from zope.viewlet.interfaces import IViewletManager, IViewlet
from Acquisition import aq_inner
from plone.app.viewletmanager.manager import BaseOrderedViewletManager
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.i18n.locales.interfaces import IContentLanguageAvailability
from plone.i18n.locales.languages import LanguageAvailability
from Products.Five.browser import BrowserView as View
from Products.CMFCore.utils import getToolByName
from Products.PloneLanguageTool import LanguageTool
from vnccollab.theme.tests.base import FunctionalTestCase


class TestActionMenuView(FunctionalTestCase):
    def test_languages(self):
        self.tool_id = LanguageTool.id
        self.ltool = self.portal._getOb(self.tool_id)

        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                   setContentN=False,
                                   setCookieN=False, setCookieEverywhere=False,
                                   setRequestN=False,
                                   setPathN=False, setForcelanguageUrls=False,
                                   setAllowContentLanguageFallback=True,
                                   setUseCombinedLanguageCodes=True,
                                   startNeutral=False, displayFlags=False,
                                   setCcTLDN=True, setSubdomainN=True,
                                   setAuthOnlyN=True)

        #lang_avail = LanguageAvailability()

        #sm = getSiteManager()
        #sm.registerUtility(lang_avail, provided=IContentLanguageAvailability)
        browser = self.login()
        #http://127.0.0.1:8080/Plone/switchLanguage?set_language=de
        browser.open(self.portal_url + '/switchLanguage?set_language=de')
        # print browser.contents

        #vnccollab.theme.languageselector
        request = self.app.REQUEST
        context = self.portal
        view = View(context, request)

        # 'vnccollab.theme.languageselector'
        manager1 = queryMultiAdapter((context, request, view), IViewletManager, 'plone.portalheader', default=None)
        manager1.update()

        manager = BaseOrderedViewletManager()
        alsoProvides(manager, IPortalHeader)

        viewlet = queryMultiAdapter((aq_inner(context), request, view), 
            IViewletManager, name='vnccollab.theme.languageselector')
        # print " ---+--- " * 5
        # print viewlet
        # print context, request, view
        # print [v for v in manager1.viewlets]
        # print " ---+--- " * 5

        #browser.open(self.portal_url + '/@@language-controlpanel')
        #print browser.contents
        #browser.open(self.portal_url)
        #self.assertNotIn('portal-languageselector', browser.contents)
        #self.assertIn('personaltools-languageselector', browser.contents)

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
