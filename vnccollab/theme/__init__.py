from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

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
original_timezone = pytz.timezone
pytz.common_timezones.extend(ZONE_MAP.keys())
pytz.common_timezones.sort()

pytz.timezone = new_timezone
print '*'*80

