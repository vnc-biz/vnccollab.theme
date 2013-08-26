from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest
from Products.CMFCore.utils import getToolByName
from plone.app.upgrade.utils import installOrReinstallProduct
from plone import api

from vnccollab.theme.config import PROJECTNAME

DEFAULT_PROFILE = 'profile-%s:default' % PROJECTNAME


def upgrade_1103_1104(context):
    request = TestRequest()
    manager = getMultiAdapter((context, request),
                             name='manage-viewlets')
    manager.hide('plone.portaltop',
                 'vnccollab.cloudstream.addcontentarea')
    manager.show('plone.portaltop',
                 'vnccollab.theme.addcontentarea')


def upgrade_1108_1109(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(DEFAULT_PROFILE, 'jsregistry',
                                   run_dependencies=False)
    setup.runImportStepFromProfile(DEFAULT_PROFILE, 'cssregistry',
                                   run_dependencies=False)
    portal = api.portal.get()
    installOrReinstallProduct(portal, 'collective.quickupload')
