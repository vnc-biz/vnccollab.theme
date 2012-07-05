from zope import schema
from zope.interface import implements, alsoProvides, Interface, Invalid
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile


from z3c.form import form, field, button
import z3c.form.interfaces
from plone.z3cform.layout import FormWrapper, wrap_form

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

class NewTicketFormBase(form.Form):
    """New Ticket Base Form. It's just a selector."""
    implements(INewTicketForm)
    fields = field.Fields(INewTicketForm)
    ignoreContext = True
    label = _(u'New Ticket')
    description = u'Allows you to create a Redmine Ticket or Zimbra Task.'
    id = 'new_ticket_form'

    def updateWidgets(self):
        form.Form.updateWidgets(self)
        if (('redmine_task_form.buttons.create' in  self.request.form)
                or ('zimbra_task_form.buttons.create' in self.request.form)):
            # Shows subform selector only first time
            self.widgets['type_of_ticket'].mode = z3c.form.interfaces.HIDDEN_MODE


class ZimbraTaskFormWrapper(FormWrapper):
    """Wrapper form for New Zimbra Task"""
    form = ZimbraTaskForm


class FileTicketFormWrapper(FormWrapper):
    """Wrapper form for New Redmine Ticket"""
    form = FileTicketForm


class NewTicketForm(FormWrapper):
    """Wrapper form for New Task. It combines Zimbra and Redmine Forms."""
    form = NewTicketFormBase
    index = FiveViewPageTemplateFile('templates/newticket.pt')

    def __init__(self, context, request):
        FormWrapper.__init__(self, context, request)
        self.context = context
        self.request = request
        self.zimbra = ZimbraTaskFormWrapper(context, request)
        self.redmine = FileTicketFormWrapper(context, request)

    def update(self):
        FormWrapper.update(self)
        if 'redmine_task_form.buttons.create' not in self.request.form:
            # Shows zimbra form only if redmine was not chosen
            self.zimbra.update()
        if 'zimbra_task_form.buttons.create' not in self.request.form:
            # Shows redmine form only if zimbra was not chosen
            self.redmine.update()


