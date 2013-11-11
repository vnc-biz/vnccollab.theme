from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.tableview import Table

messageFactory = MessageFactory('vnccollab.theme')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

def new_timezone(zone):
    ''' Monkey patching replacement for pytz.timezone'''
    zone = ZONE_MAP.get(zone, zone)
    return original_timezone(zone)


# Granting permissions for importing zope.component in python scripts
ModuleSecurityInfo("zope.component").declarePublic("getMultiAdapter")
ModuleSecurityInfo("vnccollab.common.livesearch").declarePublic("get_query")


# Monkey patching pytz.timezone and pytz.commont_timezones

print '*'*80
print 'Patching pytz'
ZONE_MAP = {'Asia/Mumbai': 'Asia/Kolkata',}

import pytz
if pytz.timezone.__doc__ != ' Monkey patching replacement for pytz.timezone':
    original_timezone = pytz.timezone
    pytz.common_timezones.extend(ZONE_MAP.keys())
    pytz.common_timezones.sort()

    pytz.timezone = new_timezone
    print '*'*80

# Manual monkey patching Override render from Table

Table.render = ViewPageTemplateFile("browser/templates/table.pt")

