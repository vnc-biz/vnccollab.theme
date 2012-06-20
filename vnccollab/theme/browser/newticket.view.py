from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from vnccollab.theme import messageFactory as _
from vnccollab.theme.browser.file_issue import FileTicketForm

class NewTicketForm(BrowserView):
    """
    """
    render = ViewPageTemplateFile('templates/newticket.pt')

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.setItems()

    def __call__(self):
        return self.render()

    def setItems(self):
        import pdb;pdb.set_trace()
        redmine = FileTicketForm(self.context, self.request)
        redmine.update()
        xxx = redmine.render()
        return [('redmine', 'redmine'),
                ('zimbra', 'zimbra')]

