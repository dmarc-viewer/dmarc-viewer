"""
<Program Name>
    widgets.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    August, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Custom widgets to be used with django's model form magic, i.e. to create
    auto-forms based on the model. See website.forms for more infos.

"""
from django import forms
from django.forms.widgets import SelectMultiple, TextInput
from django.utils.safestring import mark_safe


class MultiSelectWidget(SelectMultiple):
    """Multi Select Widget using Selectize.js. If `load` is passed, selectize
    receives extra options to load select options dynamically from the
    passed `action` url. """

    def __init__(self, *args, **kwargs):
        self.load = kwargs.pop("load")
        self.action = kwargs.pop("action")
        super(MultiSelectWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        # If the widget loads choices dynamically we add a custom class
        if self.load:
            if not isinstance(attrs, dict):
                attrs = {}
            attrs["class"] = attrs.get("class", "") + " selectize-dynamic"

        html = super(MultiSelectWidget, self).render(name, value, attrs,
                renderer)
        js   =  '''<script type="text/javascript">
                    (function($){
                        var options = {
                            loadingClass: "selectize-loading"
                        };
                        if (%(load)r){
                            options.onType = editor.loadChoices;
                            options.load_action = "%(action)s";
                            options.load_choice_type = "%(load)s";
                            }
                        // Also gets called when the widget is cloned
                        $(document).ready(function(){
                            $('#id_%(name)s').selectize(options);
                        });
                    })('django' in window && django.jQuery ? django.jQuery: jQuery);
                </script>''' % {'load' : self.load, 'name': name,
                        'action': self.action}

        return  mark_safe("%s %s" % (html, js))


class ColorPickerWidget(TextInput):
    """Color Picker for HTML5 input type color, using bootstrap-colorpicker.js
    as fallback. """
    input_type = 'color'

    def render(self, name, value, attrs=None, renderer=None):
        if not value:
            value = "#006699"
        html = super(ColorPickerWidget, self).render(name, value, attrs,
                renderer)
        js   =  '''<script type="text/javascript">
                    (function($){
                        $(document).ready(function(){
                            $('#id_%s').each(function(idx, el){
                                if (el.type != 'color')
                                    $(el).colorpicker();
                            });
                        });
                    })('django' in window && django.jQuery ? django.jQuery: jQuery);
                </script>''' % name
        return  mark_safe("%s %s" % (html, js))


class DatePickerWidget(TextInput):
    """Bootstrap Datepicker Widget """
    input_type = 'date'

    def render(self, name, value, attrs=None, renderer=None):
        html = super(DatePickerWidget, self).render(name, value, attrs,
                renderer)
        js   =  '''<script type="text/javascript">
                    (function($){
                        $(document).ready(function(){
                            $('#id_%s').each(function(idx, el){
                                if (el.type != 'date')
                                    $(el).datepicker();
                            });
                        });
                    })('django' in window && django.jQuery ? django.jQuery: jQuery);
                </script>''' % name
        return  mark_safe("%s %s" % (html, js))