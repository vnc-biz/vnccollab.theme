from Products.CMFCore.utils import getToolByName

from .config import PROJECTNAME

DEFAULT_PROFILE = 'profile-%s:default' % PROJECTNAME


def upgrade_addbuttonviewlet(context):
    '''Adds AddButtonViewlet.'''
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(DEFAULT_PROFILE, 'viewlets',
        run_dependencies=False)
