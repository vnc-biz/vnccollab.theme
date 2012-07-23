from zope.interface import implements, Interface
from zope import schema

from plone.app.registry.browser import controlpanel

from vnccollab.theme import messageFactory as _


class IWorldClockSettings(Interface):

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
       values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc',
           'vncHeaderViewlet'),
       default='vncHeaderViewlet')

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
        default='Asia/Mumbai')

    skin_2 = schema.Choice(
       title=_(u"Clock 2 Skin"),
       description=u'',
       required=True,
       values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc',
           'vncHeaderViewlet'),
       default='vncHeaderViewlet')

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
        default='America/New_York')

    skin_3 = schema.Choice(
       title=_(u"Clock 3 Skin"),
       description=u'',
       required=True,
       values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc',
           'vncHeaderViewlet'),
       default='vncHeaderViewlet')

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


class WorldClockSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IWorldClockSettings
    label  = _(u'WorldClock Settings')
    description = _(u'')

    def updateFields(self):
        super(WorldClockSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(WorldClockSettingsEditForm, self).updateWidgets()

class WorldClockSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = WorldClockSettingsEditForm


class IOpenERPSettings(Interface):
    ''' Global OpenERP Settings.

    Here you define that action ids associate with the database.
    '''
    openerpActions = schema.List(
            title = u'OpenERP Actions',
            description = u"Actions, one for line in the format 'id,description'. "
                          u"DO NOT use commas in the description",
            value_type = schema.TextLine(),
            required = True,
            default = [],
            )


class OpenERPSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IOpenERPSettings
    label = u'OpenERP Settings'
    description = _(u"""""")

    def updateFields(self):
        super(OpenERPSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(OpenERPSettingsEditForm, self).updateWidgets()


class OpenERPSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
        form = OpenERPSettingsEditForm
