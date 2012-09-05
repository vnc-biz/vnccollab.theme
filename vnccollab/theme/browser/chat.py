from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ChatView(BrowserView):
    """
    """

    template = ViewPageTemplateFile('templates/chat.pt')

    def __call__(self):
        return self.template()
