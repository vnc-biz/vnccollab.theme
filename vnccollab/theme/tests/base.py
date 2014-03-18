import transaction

from DateTime import DateTime
import unittest2 as unittest

from Acquisition import aq_base

from Testing.ZopeTestCase import user_name
from plone.testing.z2 import Browser
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.controlpanel.security import ISecuritySchema

from Products.CMFCore.utils import getToolByName

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager

from vnccollab.theme.testing import VNCCOLLAB_THEME_INTEGRATION_TESTING, \
    VNCCOLLAB_THEME_FUNCTIONAL_TESTING

from Products.PloneTestCase import utils


class BaseTestCase(unittest.TestCase):
    """Base class for tests."""

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        security_adapter =  ISecuritySchema(self.portal)
        security_adapter.set_enable_user_folders(True)
        self.app = self.layer['app']
        self.portal_url = self.portal.absolute_url()
        self.membership = getToolByName(self.portal, 'portal_membership') 
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.request = self.app.REQUEST

        # create members if needed
        if hasattr(self, 'members') and self.members:
            for member in self.members:
                self.addMember(*member)

        if not hasattr(aq_base(self.portal), 'acl_users'):
            self.portal.manage_addUserFolder()

    def login(self, user_name=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        """Helper method for login."""
        browser = Browser(self.portal)

        # Get an account and login via the login form.
        browser.open(self.portal_url + '/login_form')

        browser.getControl(name='__ac_name', index=0).value = user_name
        browser.getControl(name='__ac_password', index=0).value = TEST_USER_PASSWORD
        browser.getControl(name='submit', index=0).click()

        return browser

    def setRoles(self, roles, name=user_name):
        '''Changes the user's roles.'''
        uf = self.portal.acl_users
        uf.userFolderEditUser(name, None, utils.makelist(roles), [])
        if name == getSecurityManager().getUser().getId():
            self._login(name)

    def _login(self, name=user_name):
        '''Logs in.'''
        uf = self.portal.acl_users
        user = uf.getUserById(name)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

    def logout(self, browser):
        """Helper method for logout."""
        browser.open(self.portal_url + '/logout')

    def addMember(self, password, fullname, email, roles, last_login_time):
        """Helper method for creating a new member."""
        self.membership.addMember(email, password, roles, [])
        member = self.membership.getMemberById(email)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time)})
        transaction.commit()


class IntegrationTestCase(BaseTestCase):
    """Base class for integration tests."""

    layer = VNCCOLLAB_THEME_INTEGRATION_TESTING


class FunctionalTestCase(BaseTestCase):
    """Base class for functional tests."""

    layer = VNCCOLLAB_THEME_FUNCTIONAL_TESTING
