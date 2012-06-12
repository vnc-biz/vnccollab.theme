from pytz import timezone
from datetime import datetime

from zope.formlib import form
from zope.interface import implements, Interface
from zope import schema
from Acquisition import aq_inner
from zope.component import getUtility, getMultiAdapter, queryMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager, IPortletRenderer
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize

from vnccollab.theme.portlets import redmine_tickets
from vnccollab.theme import messageFactory as _


class IDashletPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Header"),
        description=_(u"Header of the portlet."),
        required=True,
        default=u'My Dashlet')

    count = schema.Int(title=_(u'Number of items to display'),
        description=_(u'How many items to list.'),
        required=True,
        default=5)


class Assignment(base.Assignment):
    implements(IDashletPortlet)

    header = u'My Dashlet'
    count = 5

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=u'My Dashlet', count=5):
        self.header = header
        self.count = count


class Renderer(base.Renderer):
    render = ZopeTwoPageTemplateFile('templates/dashlet.pt')


class AddForm(base.AddForm):
    form_fields = form.Fields(IDashletPortlet)
    label = _(u"Add Dashlet portlet")
    description = _(u"A portlet displaying news, messages, articles...")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IDashletPortlet)
    label = _(u"Edit Dashlet portlet")
    description = _(u"A portlet displaying news, messages, articles...")