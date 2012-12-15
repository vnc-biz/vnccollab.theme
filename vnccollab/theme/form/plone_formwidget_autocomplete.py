from AccessControl import getSecurityManager
from AccessControl import ClassSecurityInfo
from Acquisition import Explicit
from Acquisition.interfaces import IAcquirer
from App.class_init import InitializeClass
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import z3c.form.interfaces
import z3c.form.widget
import z3c.form.util
from z3c.formwidget.query.widget import QuerySourceRadioWidget
from z3c.formwidget.query.widget import QuerySourceCheckboxWidget
from zope.interface import implementsOnly, implementer

from plone.formwidget.autocomplete.interfaces import IAutocompleteWidget
from plone.formwidget.autocomplete import widget as base


# vipod: customize JavaScript template to work with jQuery UI autocomplete
js_template = """\
(function($) {
    $().ready(function() {
        $('#%(id)s-input-fields').data('klass','%(klass)s').data('title','%(title)s').data('input_type','%(input_type)s');
        $('#%(id)s-buttons-search').remove();
        $('#%(id)s-widgets-query').autocomplete({
            source: function(request, response){
              var suggest = [];
              $.ajax({
                'url': '%(url)s',
                'type': 'get',
                'data': {'q': request.term},
                'dataType': 'text',
                'async': false,
                'success': function(data, statux, xhr) {
                  var items = data.split("\\n");
                  for (var i=0,o;o=items[i];i++) {
                    var parts = o.split('|');
                    suggest.push({'label':parts[1],'value':parts[0]});
                  }
                },
              });
              return response(suggest);
            },
            minLength: %(minChars)d,
            select: %(js_callback)s
        });
        %(js_extra)s
    });
})(jQuery);
    """


class AutocompleteSelectionWidget(base.AutocompleteBase,
    QuerySourceRadioWidget):
    """Autocomplete widget that allows single selection.
    """

    klass = u'autocomplete-selection-widget'
    input_type = 'radio'
    js_template = js_template

class AutocompleteMultiSelectionWidget(base.AutocompleteBase,
                                       QuerySourceCheckboxWidget):
    """Autocomplete widget that allows multiple selection
    """

    klass = u'autocomplete-multiselection-widget'
    input_type = 'checkbox'
    js_template = js_template

@implementer(z3c.form.interfaces.IFieldWidget)
def AutocompleteFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field,
        AutocompleteSelectionWidget(request))


@implementer(z3c.form.interfaces.IFieldWidget)
def AutocompleteMultiFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field,
        AutocompleteMultiSelectionWidget(request))
