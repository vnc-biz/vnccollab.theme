import logging
import time
from pytz import common_timezones
from pyactiveresource.activeresource import ActiveResource

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from plone.registry.interfaces import IRegistry
from plone.memoize import ram

from vnccollab.theme import messageFactory as _
from vnccollab.theme.portlets.zimbra_mail import logException
from vnccollab.theme.config import REDMINE_ENUMERATORS_CACHE_TIME


logger = logging.getLogger('vnccollab.theme.redmine_enumerator_vocabularies')

def cachemethod(interval):
    def _cachekey(method, self, *args):
        """Time and settings based cache"""
        return hash(tuple(list(args) + [interval]))
    return _cachekey

@ram.cache(cachemethod(time.time() // REDMINE_ENUMERATORS_CACHE_TIME))
def getRedmineEnumerators(url, username, password):
    """Returns redmine enumerators:

    * projects
    * trackers
    * priorities
    * users
    """
    data = {}
    # projects, result is sensitive to user, so only those projects are returned
    # where current logged in user has an access
    projects = []
    Project = type("Project", (ActiveResource,), {'_site': url, '_user':
            username, '_password': password})
    for item in Project.find():
        projects.append((item.id, item.name))
    # projects.sort(lambda x,y:cmp(x[1], y[1]))
    data['projects'] = tuple(projects)

    # trackers
    # TODO: redmine 1.1 do not support tracker REST API call, so also hard-code
    # it so far
    # trackers = []
    # Tracker = type("Tracker", (ActiveResource,), {'_site': url, '_user':
    #         username, '_password': password})
    # for item in Tracker.find():
    #     trackers.append((item.id, item.name))
    # trackers.sort(lambda x,y:cmp(x[1], y[1]))
    # data['trackers'] = tuple(trackers)
    data['trackers'] = (('1', 'Bug'), ('2', 'Feature'), ('3', 'Support'),
        ('4', 'WR - Work Request'), ('5', 'CR - Change Request'),
        ('6', 'Status Call'), ('7', 'Meeting'), ('10', 'Draft'),
        ('11', 'Sign-Off'), ('12', 'Approval'), ('13', 'Testing'))

    # priorities
    # TODO: switch to using REST API after this ticket is closed:
    #         http://www.redmine.org/issues/7402
    #       for now we are just hard-coding this list
    # priorities = []
    # IssuePriority = type("IssuePriority", (ActiveResource,), {'_site': url,
    #     '_user': username, '_password': password})
    # for item in IssuePriority.find():
    #     priorities.append((item.id, item.name))
    # priorities.sort(lambda x,y:cmp(x[1], y[1]))
    # data['priorities'] = tuple(priorities)
    data['priorities'] = (('3', 'Low'), ('4', 'Normal'), ('5', 'High'),
        ('6', 'Urgent'), ('7', 'Immediate'))

    # users
    users = []
    User = type("User", (ActiveResource,), {'_site': url, '_user':
            username, '_password': password})

    # only Redmine Administrator could do this call
    try:
        for item in User.find():
            users.append((item.id, '%s %s' % (item.firstname, item.lastname)))
    except Exception, e:
        pass

    users.sort(lambda x,y:cmp(x[1], y[1]))
    data['users'] = tuple(users)

    return data

class RedmineVocabularyFactory(object):

    implements(IVocabularyFactory)

    def __init__(self, resource):
        self.resource = resource

    def __call__(self, context):
        # get authenticated user
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        if not member:
            return SimpleVocabulary([])

        username, password = member.getProperty('redmine_username', ''), \
            safe_unicode(member.getProperty('redmine_password',
            '')).encode('utf-8')
        registry = getUtility(IRegistry)
        url = registry.get('vnccollab.theme.redmine.url')
        field_id = registry.get(
            'vnccollab.theme.redmine.plone_uid_field_id')
        if not (username and password and url and field_id):
            return SimpleVocabulary([])

        try:
            data = getRedmineEnumerators(url, username, password)
        except Exception, e:
            logException(_(u"Error during fetching redmine enumerators"),
                context=context, logger=logger)
            return SimpleVocabulary([])

        return SimpleVocabulary([SimpleTerm(key, key, value)
            for key, value in data.get(self.resource, ())])

ProjectsRedmineVocabulary = RedmineVocabularyFactory('projects')
TrackersRedmineVocabulary = RedmineVocabularyFactory('trackers')
PrioritiesRedmineVocabulary = RedmineVocabularyFactory('priorities')
UsersRedmineVocabulary = RedmineVocabularyFactory('users')

class TimeZonesVocabularyFactory(object):
    """Returns list of common timezones with user friendly titles.

    It uses python timezone library: pytz.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        for zone_name in common_timezones:
            # prepare zone title: America/New_York -> America/New York
            terms.append(SimpleTerm(zone_name, zone_name,
                zone_name.replace('_', ' ')))

        return SimpleVocabulary(terms)

TimeZonesVocabulary = TimeZonesVocabularyFactory()

from Products.CMFCore.utils import getToolByName

class ATLinkVocabularyFactory(object):
    '''Return vocabulary with references to ATLink objects'''
    implements(IVocabularyFactory)

    def __call__(self, context):
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog.searchResults(Type = 'Link')
        terms = [SimpleTerm(value=x.getObject(),
                            token=x.UID,
                            title=x.getObject().Title())
                        for x in brains]
        return SimpleVocabulary(terms)

ATLinkVocabulary = ATLinkVocabularyFactory()
