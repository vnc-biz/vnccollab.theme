from pytz import timezone
from datetime import datetime

from zope.formlib import form
from zope.interface import implements, Interface
from zope import schema

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from vnccollab.theme import messageFactory as _


class IWorldClockPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Header"),
        description=_(u"Header of the portlet."),
        required=True,
        default=u'World Clocks')

    tz_1 = schema.Choice(
        title=_(u"Clock 1 Timezone"),
        description=u'',
        required=True,
        vocabulary='vnccollab.theme.vocabularies.TimeZonesVocabulary',
        default='Europe/Berlin')

    skin_1 = schema.Choice(
       title=_(u"Clock 1 Skin"),
       description=u'',
       required=True,
       values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc'),
       default='vnc')

    radius_1 = schema.Int(
        title=_(u"Clock 1 Radius"),
        description=u'',
        required=True,
        default=35)

    no_seconds_1 = schema.Bool(
        title=_(u"Clock 1 Without Seconds"),
        description=_(u"Do not show seconds handle."),
        required=False,
        default=False)

    tz_2 = schema.Choice(
        title=_(u"Clock 2 Timezone"),
        description=u'',
        required=False,
        vocabulary='vnccollab.theme.vocabularies.TimeZonesVocabulary',
        default='Europe/Berlin')

    skin_2 = schema.Choice(
       title=_(u"Clock 2 Skin"),
       description=u'',
       required=True,
       values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc',
           'vncHeaderViewlet'),
       default='vnc')

    radius_2 = schema.Int(
        title=_(u"Clock 2 Radius"),
        description=u'',
        required=False,
        default=35)

    no_seconds_2 = schema.Bool(
        title=_(u"Clock 2 Without Seconds"),
        description=_(u"Do not show seconds handle."),
        required=False,
        default=False)

    tz_3 = schema.Choice(
        title=_(u"Clock 3 Timezone"),
        description=u'',
        required=False,
        vocabulary='vnccollab.theme.vocabularies.TimeZonesVocabulary',
        default='Europe/Berlin')

    skin_3 = schema.Choice(
       title=_(u"Clock 3 Skin"),
       description=u'',
       required=True,
       values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc'),
       default='vnc')

    radius_3 = schema.Int(
        title=_(u"Clock 3 Radius"),
        description=u'',
        required=False,
        default=35)

    no_seconds_3 = schema.Bool(
        title=_(u"Clock 3 Without Seconds"),
        description=_(u"Do not show seconds handle."),
        required=False,
        default=False)

class Assignment(base.Assignment):
    implements(IWorldClockPortlet)

    header = u'World Clock'
    tz_1 = 'Europe/Berlin'
    skin_1 = 'vnc'
    radius_1 = 35
    no_seconds_1 = False
    tz_2 = 'Europe/Berlin'
    skin_2 = 'vnc'
    radius_2 = 35
    no_seconds_2 = False
    tz_3 = 'Europe/Berlin'
    skin_3 = 'vnc'
    radius_3 = 35
    no_seconds_3 = False

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=_(u"World Clock"), tz_1='Europe/Berlin',
        skin_1='vnc', radius_1=35, no_seconds_1=False, tz_2='Europe/Berlin',
        skin_2='vnc', radius_2=35, no_seconds_2=False, tz_3='Europe/Berlin',
        skin_3='vnc', radius_3=35, no_seconds_3=False):
        self.header = header
        self.tz_1 = tz_1
        self.skin_1 = skin_1
        self.radius_1 = radius_1
        self.no_seconds_1 = no_seconds_1
        self.tz_2 = tz_2
        self.skin_2 = skin_2
        self.radius_2 = radius_2
        self.no_seconds_2 = no_seconds_2
        self.tz_3 = tz_3
        self.skin_3 = skin_3
        self.radius_3 = radius_3
        self.no_seconds_3 = no_seconds_3

class Renderer(base.Renderer):

    render = ZopeTwoPageTemplateFile('templates/world_clock.pt')

    def getTimeZoneInfo(self, zone_name):
        """Return timezone city name and hours offset"""
        if not zone_name:
            return None

        offset = datetime.now(timezone(zone_name)).utcoffset()
        hours = offset.seconds / 3600.0
        # if time delta is negative, then subtract 24 hours
        if offset.days < 0:
            hours = hours - 24.0
        return {'hours': '%.1f' % round(hours, 1),
            'city': zone_name.split('/')[-1].replace('_', ' ')}

class AddForm(base.AddForm):
    form_fields = form.Fields(IWorldClockPortlet)
    label = _(u"Add World Clock portlet")
    description = _(u"A portlet displaying analog world clocks.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IWorldClockPortlet)
    label = _(u"Edit World Clock portlet")
    description = _(u"A portlet displaying analog world clocks.")
