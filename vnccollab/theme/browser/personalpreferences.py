from plone.app.users.browser import personalpreferences as base


class UserDataPanelAdapter(base.UserDataPanelAdapter):

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
