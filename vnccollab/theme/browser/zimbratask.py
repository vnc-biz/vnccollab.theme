from zope import schema
from zope.interface import implements, Interface, Invalid
from zope.component import getMultiAdapter, getUtility

from z3c.form import form, field, button
from z3c.form.interfaces import IErrorViewSnippet
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from collective.z3cform import datetimewidget

from vnccollab.theme import messageFactory as _
from vnccollab.theme.zimbrautil import IZimbraUtil
import vnccollab.theme.util as util

class IZimbraTaskForm(Interface):
    # TODO: List Id

    # we end it with _ to avoid conflicts in newtask.py
    subject_ = schema.TextLine(
        title = _(u'Subject'),
        description = u'',
        required = True)

    location = schema.TextLine(
        title = _(u'Location'),
        description = _('Task Location'),
        required = False)

    status = schema.Choice(
        title = _(u"Status"),
        description = u'',
        vocabulary = 'vnccollab.theme.vocabularies.StatusZimbraTaskVocabulary',
        required = True)

    # we end it with _ to avoid conflicts in newtask.py
    priority_ = schema.Choice(
        title = _(u"Priority"),
        description = u'',
        vocabulary = 'vnccollab.theme.vocabularies.PrioritiesZimbraTaskVocabulary',
        default = '5',
        required = True)

    percentComplete = schema.Choice(
        title = _(u"Percentage of Completion"),
        description = u'',
        vocabulary = 'vnccollab.theme.vocabularies.PercentageZimbraTaskVocabulary',
        required = True)

    startDate = schema.Date(
        title = _(u"Start date"),
        description = u'',
        #widget = datetimewidget.DateFieldWidget,
        required = False)

    endDate = schema.Date(
        title = _(u"Due date"),
        description = u'',
        required = False)

    content = schema.Text(
        title = _(u"Description"),
        description = u'',
        required = False,
        default = u'')


class ZimbraTaskForm(form.Form):
    implements(IZimbraTaskForm)
    fields = field.Fields(IZimbraTaskForm)
    label = _("New Zimbra Task")

    formErrorsMessage = _(u"There were some errors.")
    successMessage = _(u"Task was created successfully.")

    ignoreContext = True

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

        url = util.getZimbraUrl(self.context)
        username, password = util.getZimbraCredentials(self.context)
        if not username or not password or not url:
            if not username or not password:
                msg = _(u"Please, set correct zimbra username and password in "
                "your profile form in order to create a zimbra task.")
            else:
                msg = _(u"Please, set Zimbra URL in Control "
                    " Panel (Configuration Registry).")
            # issue form level error
            self.status = msg
            error = getMultiAdapter((Invalid(u''), self.request, None,
                None, self, self.context), IErrorViewSnippet)
            error.update()
            self.widgets.errors += (error,)
            return

        created = False
        try:
            zimbraUtil = getUtility(IZimbraUtil)
            client = zimbraUtil.get_client(url, username, password)
            email = util.getZimbraEmail(self.context)
            data['author'] = email
            data['subject'] = data['subject_']
            data['priority'] = data['priority_']
            task = client.create_task(data)
            util.addZimbraAnnotatedTasks(self.context, task)
            created = True

        except Exception, e:
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
            if not created:
                self.status = _(u"Task wasn't created, please, check your "
                    "settings or contact site administrator if you are sure "
                    "your settings are set properly.")
                error = getMultiAdapter((Invalid(u''), self.request, None,
                    None, self, self.context), IErrorViewSnippet)
                error.update()
                self.widgets.errors += (error,)
                return

        self.status = self.successMessage
        IStatusMessage(self.request).addStatusMessage(self.successMessage,
            type='info')
        return self.request.response.redirect(self.context.absolute_url())

