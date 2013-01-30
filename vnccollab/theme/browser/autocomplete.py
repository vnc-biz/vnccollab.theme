import simplejson

from plone import api
from plone.memoize import instance
from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode

from vnccollab.theme.util import getZimbraClient


class EmailAutoCompleteView(BrowserView):
    '''Returns a json object with the mail infoemail of users given a string.'''

    def __call__(self):
        search = self.request.form.get('search', '').lower()
        info = self.mail_info()
        info = self.filter(info, search)
        return simplejson.dumps(info)

    def filter(self, info, search):
        return [x for x in info if (search in x[0].lower())
                                or (search in x[1].lower())]

    def mail_info(self):
        '''Returns a list with the mail info of all account associated to the
        current user.

        Each mail info is a tuple with the form

                (email, title)

        where title is a string with the form

                'Name (login) <email>'.
        '''
        plone_info = self.mail_info_from_plone()
        zimbra_info = self.mail_info_from_zimbra_address_book()

        info = plone_info[:]
        mails = [x[0] for x in info]
        for x in zimbra_info:
            if x[0] not in mails:
                info.append(x)
        info.sort(lambda x, y: cmp(x[1], y[1]))
        return info

    @instance.memoize
    def mail_info_from_plone(self):
        '''Returns the mail info from all plone users.'''
        users = api.user.get_users()
        return [_mail_info_from_user(x) for x in users]

    @instance.memoize
    def mail_info_from_zimbra_address_book(self):
        '''Returns the mail info from the zimbra address book of the current
        user.'''
        client = getZimbraClient(self.context)
        if client is None:
            return []

        address_book = client.get_address_book()
        mail_info = [_mail_info_from_zimbra(x) for x in address_book]
        mail_info = [x for x in mail_info if x is not None]
        return mail_info


def _mail_info_from_user(user):
    '''Converts a plone user into a mail info.'''
    id = user.getProperty('id')
    email = user.getProperty('email')
    name = user.getProperty('fullname')

    if id == email:
        title = '{0} <{1}>'.format(name, email)
    else:
        title = '{0} ({1}) <{2}>'.format(name, id, email)
    return (email, safe_unicode(title))


def _mail_info_from_zimbra(user):
    name = user._getAttr('fileAsStr')
    if name is None:
        return None

    # Coverts 'Surname, Name' in 'Name Surname'
    name = ' '.join([a.strip() for a in name.split(',')[::-1]])
    # TODO: How #$%"/& to get the mail?
    email = [x for x in user.a if '@' in x]
    if not email:
        return None

    email = email[0]
    # TODO: zimbra is not returning unicode
    name = safe_unicode(name)
    email = safe_unicode(email)
    title = u'{0} <{1}>'.format(name, email)
    return (email, title)
