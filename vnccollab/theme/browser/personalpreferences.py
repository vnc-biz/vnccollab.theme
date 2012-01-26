from plone.app.users.browser import personalpreferences as base


class UserDataPanelAdapter(base.UserDataPanelAdapter):

    # Zimbra
    
    def get_zimbra_username(self):
        return self._getProperty('zimbra_username')

    def set_zimbra_username(self, value):
        return self.context.setMemberProperties({'zimbra_username': value})

    zimbra_username = property(get_zimbra_username, set_zimbra_username)

    def get_zimbra_password(self):
        return self._getProperty('zimbra_password')

    def set_zimbra_password(self, value):
        return self.context.setMemberProperties({'zimbra_password': value})

    zimbra_password = property(get_zimbra_password, set_zimbra_password)

    # Etherpad

    def get_etherpad_url(self):
        return self._getProperty('etherpad_url')

    def set_etherpad_url(self, value):
        return self.context.setMemberProperties({'etherpad_url': value})

    etherpad_url = property(get_etherpad_url, set_etherpad_url)

    def get_etherpad_username(self):
        return self._getProperty('etherpad_username')

    def set_etherpad_username(self, value):
        return self.context.setMemberProperties({'etherpad_username': value})

    etherpad_username = property(get_etherpad_username, set_etherpad_username)

    def get_etherpad_password(self):
        return self._getProperty('etherpad_password')

    def set_etherpad_password(self, value):
        return self.context.setMemberProperties({'etherpad_password': value})

    etherpad_password = property(get_etherpad_password, set_etherpad_password)

    # OpenERP

    def get_openerp_username(self):
        return self._getProperty('openerp_username')

    def set_openerp_username(self, value):
        return self.context.setMemberProperties({'openerp_username': value})

    openerp_username = property(get_openerp_username, set_openerp_username)

    def get_openerp_password(self):
        return self._getProperty('openerp_password')

    def set_openerp_password(self, value):
        return self.context.setMemberProperties({'openerp_password': value})

    openerp_password = property(get_openerp_password, set_openerp_password)
