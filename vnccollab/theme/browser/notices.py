from plone.autoform.interfaces import WIDGETS_KEY

from collective.notices.browser import views as base
from collective.notices.interfaces import INotice

from ..form.plone_formwidget_autocomplete import AutocompleteMultiFieldWidget


class EditNotice(base.EditNotice):
    def updateFields(self):
        # assign our custom autocomplete widget
        tags = INotice.getTaggedValue(WIDGETS_KEY)
        tags['users_and_groups'] = AutocompleteMultiFieldWidget
        INotice.setTaggedValue(WIDGETS_KEY, tags)
        super(EditNotice, self).updateFields()

class AddNotice(base.AddNotice):
    def updateFields(self):
        # assign our custom autocomplete widget
        tags = INotice.getTaggedValue(WIDGETS_KEY)
        tags['users_and_groups'] = AutocompleteMultiFieldWidget
        INotice.setTaggedValue(WIDGETS_KEY, tags)
        super(AddNotice, self).updateFields()
