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

        browser = self.login()
        browser.open(self.portal_url + '/switchLanguage?set_language=de')

        request = self.app.REQUEST
        context = self.portal
        view = View(context, request)

        manager1 = queryMultiAdapter((context, request, view), IViewletManager, 'plone.portalheader', default=None)
        manager1.update()

        manager = BaseOrderedViewletManager()
        alsoProvides(manager, IPortalHeader)

        viewlet = queryMultiAdapter((aq_inner(context), request, view), 
            IViewletManager, name='vnccollab.theme.languageselector')
