from zope import schema
from zope.interface import implements, alsoProvides, Interface, Invalid

from z3c.form import form, field, button

from vnccollab.theme import messageFactory as _
from vnccollab.theme.vocabularies import SimpleVocabularyFactory
from vnccollab.theme.browser.zimbratask import IZimbraTaskForm, ZimbraTaskForm
from vnccollab.theme.browser.file_issue import IFileTicketForm, FileTicketForm


class INewTicketForm(Interface):
    """
    """
    type_of_ticket = schema.Choice(
        title = _(u'Type of Ticket'),
        description = _(u''),
        vocabulary = 'vnccollab.theme.vocabularies.NewTicketVocabulary',
        required = True)

class NewTicketForm(ZimbraTaskForm, FileTicketForm):
    """
    """
    implements(INewTicketForm)
    fields = (field.Fields(INewTicketForm) + field.Fields(IZimbraTaskForm)
             + field.Fields(IFileTicketForm))

    ignoreContext = True
    label = _(u'New Ticket')
    description = u'Allows you to create a Redmine Ticket or Zimbra Task.'
    id = 'new_ticket_form'

    def updateActions(self):
        ZimbraTaskForm.updateActions(self)
        self._setCssClass(ZimbraTaskForm.fields.keys(), 'zimbra-widget')
        self._setCssClass(FileTicketForm.fields.keys(), 'redmine-widget')

    def _setCssClass(self, widgetNames, class_):
        for name in widgetNames:
            self.widgets[name].addClass(class_)

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.context.absolute_url() + '/@@' + self.__name__

    @button.buttonAndHandler(_(u"Create"), name='create')
    def handleCreate(self, action):
        """Create redmine ticket using REST API."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        if data['type_of_ticket'] == 'zimbra':
            return ZimbraTaskForm.handleCreate(self, action)
        else:
            return FileTicketForm.handleCreate(self, action)
