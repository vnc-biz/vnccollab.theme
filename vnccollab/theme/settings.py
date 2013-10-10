from zope import schema
from zope.interface import Interface
from zope.component import getUtility, provideAdapter

from plone import api
from plone.registry.interfaces import IRegistry
from plone.app.registry.browser import controlpanel
from plone.autoform.form import AutoExtensibleForm
from z3c.form import form, button, datamanager
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from vnccollab.theme import messageFactory as _


provideAdapter(datamanager.DictionaryField)


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


class OpenERPSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = OpenERPSettingsEditForm


class IAnonymousHomepageSettings(Interface):
    """Anonymous Homepage Settings."""
    help_url = schema.URI(
        title=(u'Help URL'),
        description=_(u'URL of the page that shows the site help.'),
        required=False,
        )


class IAnonymousHomepageForm(IAnonymousHomepageSettings):
    """Anonymous Homepage Form."""
    logo = schema.Bytes(
        title=_(u'Homepage Logo'),
        description=_(u'Upload an image to set or replace the site logo'),
        required=False,
        )

    delete_logo = schema.Bool(
        title=_(u"Delete Logo"),
        description=_(u"Delete the customized logo."),
        required=False,
        default=False)


class AnonymousHomepageSettingsEditForm(AutoExtensibleForm, form.EditForm):
    schema = IAnonymousHomepageForm
    label = u'Anonymous Homepage Settings'
    description = _(u"""""")

    # Internal fields: not to be configured.
    control_panel_view = "plone_control_panel"
    registry_key_base = 'vnccollab.theme.settings.IAnonymousHomepageSettings'
    help_url_key = '{0}.help_url'.format(registry_key_base)

    def getContent(self):
        registry = getUtility(IRegistry)
        help_url = registry[self.help_url_key]
        return {'help_url': help_url}

    def applyChanges(self, data):
        registry = getUtility(IRegistry)
        help_url = data['help_url']
        delete_logo = data['delete_logo']
        logo = data['logo']

        registry[self.help_url_key] = help_url

        portal = api.portal.get()
        custom_skin = portal.portal_skins.custom
        destination = custom_skin

        if delete_logo or logo:
            current_logo = api.content.get(path='/portal_skins/custom/logo.png')
            if current_logo:
                # logo.png could be not defined in ZODB, so current_logo
                # could be not None and not deleteable
                try:
                    api.content.delete(current_logo)
                except:
                    pass

        if logo:
            destination.manage_addProduct['OFSP'].manage_addImage('logo.png', logo)

    def updateActions(self):
        super(AutoExtensibleForm, self).updateActions()
        self.actions['save'].addClass("context")
        self.actions['cancel'].addClass("standalone")

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved."), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled."), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_(u'Edit Home Page'), name='edit')
    def handleEdit(self, action):
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), '@@manage-group-dashboard?key=AnonymousUsers'))


class AnonymousHomepageSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    index = ViewPageTemplateFile('browser/templates/anonhomepage_controlpanel_layout.pt')
    form = AnonymousHomepageSettingsEditForm
