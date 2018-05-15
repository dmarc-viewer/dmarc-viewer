from django import forms
from django.forms.widgets import SelectMultiple, TextInput
from django.utils.safestring import mark_safe



class MultiSelectWidget(SelectMultiple):
    """Simple Multi Select using Selectize.js """

    def __init__(self, *args, **kwargs):
        self.load = kwargs.pop("load")
        super(MultiSelectWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if self.load:
        html = super(MultiSelectWidget, self).render(name, value, attrs)
            if not isinstance(attrs, dict):
                attrs = {}
            attrs["class"] = attrs.get("class", "") + " selectize-dynamic"

        js   =  '''<script type="text/javascript">
                    (function($){
                        var options = {
                            loadingClass: "selectize-loading"
                        };
                        if (%(load)r){
                            options.onType = editor.loadChoices;
                            options.load_choice_type = "%(load)s";
                            }
                        // Also gets called when the widget is cloned
                        $(document).ready(function(){
                            $('#id_%(name)s').selectize(options);
                        });
                    })('django' in window && django.jQuery ? django.jQuery: jQuery);
                </script>''' % {'load' : self.load, 'name': name}
        return  mark_safe("%s %s" % (html, js))


class ColorPickerWidget(TextInput):
    """Color Picker for html5 input type color, using
    bootstrap-colorpicker.js as fallback. """
    input_type = 'color'

    def render(self, name, value, attrs=None):
        if not value:
            value = "#006699"
        html = super(ColorPickerWidget, self).render(name, value, attrs)
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
    """bootstrap datepicker"""
    input_type = 'date'

    def render(self, name, value, attrs=None):
        html = super(DatePickerWidget, self).render(name, value, attrs)
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