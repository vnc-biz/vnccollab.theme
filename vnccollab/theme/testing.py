import sys
import transaction
from StringIO import StringIO

from zope.interface import alsoProvides
from zope.publisher.browser import setDefaultSkin
from z3c.form.interfaces import IFormLayer
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.HTTPRequest import HTTPRequest

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing import z2

from zope.configuration import xmlconfig

try:
    import vnccollab.cloudcast
except ImportError:
    CAST_ENABLED = False
else:
    CAST_ENABLED = True


class VNCThemeContent(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        depedencies = ['collective.customizablePersonalizeForm',
                       'collective.vaporisation', 'collective.quickupload',
                       'plone.formwidget.autocomplete', 'Products.Carousel',
                       'vnccollab.theme', 'collective.autopermission',
                       'plone.app.iterate'] #, 'plone.i18n', 'plone.app.i18n']

        if CAST_ENABLED:
            depedencies.extend([
                #'collective.customizablePersonalizeForm',
                'plone.api', 'plone.app.discussion',
                'collective.prettydate', 'five.grok',
                'collective.autogroup','vnccollab.cloudcast',
                'vnccollab.cloudmobile'])

        for package in depedencies:
            module = __import__(package, fromlist=[''])
            self.loadZCML(package=module)

        if CAST_ENABLED:
            z2.installProduct(app, 'vnccollab.cloudcast')

        z2.installProduct(app, 'vnccollab.theme')
        z2.installProduct(app, 'Products.PythonScripts')

    def setUpPloneSite(self, portal):
        # Installs all the Plone stuff. Workflows etc.
        self.applyProfile(portal, 'Products.CMFPlone:plone')
        # Install portal content. Including the Members folder!
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')
        self.applyProfile(portal, 'vnccollab.theme:default')
        if CAST_ENABLED:
            self.applyProfile(portal, 'vnccollab.cloudcast:default')


VNCCOLLAB_THEME_FIXTURE = VNCThemeContent()
VNCCOLLAB_THEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(VNCCOLLAB_THEME_FIXTURE,),
    name='VNCThemeContent:Integration')
VNCCOLLAB_THEME_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(VNCCOLLAB_THEME_FIXTURE,),
    name='VNCThemeContent:Functional')


def setObjDate(obj, dt):
    """Prevent update of modification date 
       during reindexing"""
    obj.setCreationDate(dt)
    obj.setEffectiveDate(dt)
    obj.setModificationDate(dt)
    od = obj.__dict__
    od['notifyModified'] = lambda *args: None
    obj.reindexObject()
    del od['notifyModified']


def createObject(context, _type, id, delete_first=True, check_for_first=False,
                 object_date=None, **kwargs):
    result = None
    if delete_first and id in context.objectIds():
        context.manage_delObjects([id])
    if not check_for_first or id not in context.objectIds():
        result = context[context.invokeFactory(_type, id, **kwargs)]
    else:
        result = context[id]

    if object_date:
        setObjDate(result, object_date)

    transaction.commit()
    return result
