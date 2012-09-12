import logging
from pyactiveresource.activeresource import ActiveResource

from Acquisition import aq_inner
from ZODB.POSException import ConflictError

from zope import schema
from zope.component import getMultiAdapter, getUtility
from zope.interface import implements, Interface, Invalid
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage

from z3c.form import form, field, button
from z3c.form.interfaces import IErrorViewSnippet
from plone.z3cform.layout import wrap_form
from plone.registry.interfaces import IRegistry
from plone.memoize.instance import memoize
from plone.memoize import ram

from collective.z3cform.datepicker.widget import DatePickerFieldWidget

from vnccollab.theme import messageFactory as _
from vnccollab.theme.portlets.zimbra_mail import logException


logger = logging.getLogger('vnccollab.theme.redmine_file_ticket')


# TODO: display error message above form


class IFileTicketForm(Interface):

    project = schema.Choice(
        title=_(u"Project"),
        description=_(u"Pick project to post issue to."),
        vocabulary='vnccollab.theme.vocabularies.ProjectsRedmineVocabulary',
        required=True)

    tracker = schema.Choice(
        title=_(u"Tracker"),
        description=u'',
        vocabulary='vnccollab.theme.vocabularies.TrackersRedmineVocabulary',
        required=True)

    subject = schema.TextLine(
        title=_(u"Subject"),
        description=u'',
        required=True)

    description = schema.Text(
        title=_(u"Description"),
        description=u'',
        required=False,
        default=u'')

    priority = schema.Choice(
        title=_(u"Priority"),
        description=u'',
        vocabulary='vnccollab.theme.vocabularies.PrioritiesRedmineVocabulary',
        required=True)

    asignee = schema.Choice(
        title=_(u"Asignee"),
        description=u'',
        vocabulary='vnccollab.theme.vocabularies.UsersRedmineVocabulary',
        required=False)

    start_date = schema.Date(
        title=_(u"Start date"),
        description=u'',
        required=False)

    due_date = schema.Date(
        title=_(u"Due date"),
        description=u'',
        required=False)

    estimated_time = schema.ASCIILine(
        title=_(u"Estimated time (hours)"),
        description=u'',
        required=False)


class FileTicketForm(form.Form):

    implements(IFileTicketForm)

    ignoreContext = True
    label = _(u"New Issue")
    #description = u'This form will post new redmine issue.'
    id = 'file_ticket_form'
    prefix = 'redmine_task_form'

    formErrorsMessage = _(u"There were some errors.")
    successMessage = _(u"Ticket was created successfully.")

    fields = field.Fields(IFileTicketForm)

    fields['start_date'].widgetFactory = DatePickerFieldWidget
    fields['due_date'].widgetFactory = DatePickerFieldWidget

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

        # check user redmine credentials and redmine url/field id
        registry = getUtility(IRegistry)
        url = registry.get('vnccollab.theme.redmine.url')
        field_id = registry.get('vnccollab.theme.redmine.plone_uid_field_id')
        username, password = self.getAuthCredentials()
        if not username or not password or not url or not field_id:
            if not username or not password:
                msg = _(u"Please, set correct redmine username and password in "
                "your profile form in order to create redmine issue.")
            else:
                msg = _(u"Please, set Redmine URL and ID settings in Control "
                    " Panel (Configuration Registry).")

            # issue form level error
            self.status = msg
            error = getMultiAdapter((Invalid(u''), self.request, None,
                None, self, self.context), IErrorViewSnippet)
            error.update()
            self.widgets.errors += (error,)
            return

        # finally trying to post new issue
        Issue = type("Issue", (ActiveResource,), {'_site': url, '_user':
            username, '_password': password})
        try:
            start_date = data.get('start_date') or ''
            if start_date:
                start_date = start_date.strftime('%Y-%m-%d')
            due_date = data.get('due_date') or ''
            if due_date:
                due_date = due_date.strftime('%Y-%m-%d')

            issue = Issue({
                'project_id': data['project'],
                'subject': data['subject'].encode('utf-8'),
                'tracker_id': data['tracker'],
                'description': (data.get('description') or u'').encode('utf-8'),
                'priority_id': data['priority'],
                'assigned_to_id': data.get('asignee') or '',
                'start_date': start_date,
                'due_date': due_date,
                'estimated_hours': data.get('estimated_time') or '',
                'custom_fields': [{'value': self.context.UID(),
                    'id': '%d' % field_id}]
            })
            created = issue.save()
        except Exception, e:
            # issue form level error
            logException(_(u"Error during creating redmine issue at %s" %
                self.context.absolute_url()), context=self.context,
                logger=logger)
            plone_utils = getToolByName(self.context, 'plone_utils')
            exception = plone_utils.exceptionString()
            self.status = _(u"Unable create issue: ${exception}",
                mapping={u'exception' : exception})
            error = getMultiAdapter((Invalid(u''), self.request, None,
                None, self, self.context), IErrorViewSnippet)
            error.update()
            self.widgets.errors += (error,)
            return
        else:
            # check if issue was created successfully
            if not created:
                self.status = _(u"Issue wasn't created, please, check your "
                    "settings or contact site administrator if you are sure "
                    "your settings are set properly.")
                error = getMultiAdapter((Invalid(u''), self.request, None,
                    None, self, self.context), IErrorViewSnippet)
                error.update()
                self.widgets.errors += (error,)
                return

        # add status message
        self.status = self.successMessage
        IStatusMessage(self.request).addStatusMessage(self.successMessage,
            type='info')

        # redirect to success page to gather number of emailed pages
        came_from = self.request.get('HTTP_REFERER') or self.context.absolute_url()
        return self.request.response.redirect(came_from)

    @memoize
    def getAuthCredentials(self):
        """Returns username and password for redmine user."""
        # take username and password from authenticated user Zimbra creds
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        username, password = member.getProperty('redmine_username', ''), \
            member.getProperty('redmine_password', '')
        # password could contain non-ascii chars, ensure it's properly encoded
        return username, safe_unicode(password).encode('utf-8')

FileTicketFormView = wrap_form(FileTicketForm)
