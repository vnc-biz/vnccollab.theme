from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest
#from Products.CMFCore.utils import getToolByName

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
