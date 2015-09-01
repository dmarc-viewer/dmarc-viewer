from django import forms
from django.forms.widgets import SelectMultiple, TextInput
from django.utils.safestring import mark_safe

# class MultiSelectWidget(SelectMultiple):
#     """Simple Multi Select using Selectize.js"""

#     def __init__(self, attrs=None, choices=(), ):
#         super(MultiSelectWidget, self).__init__(attrs)
#         self.value      = [key for key,val in choices]
#         self.choices    = choices

#     def render(self, name, value, attrs=None):
#         html = super(MultiSelectWidget, self).render(name, self.value, attrs)
#         js   =  '''<script type="text/javascript">
#                     (function($){
#                         $(document).ready(function(){
#                             $('#id_%s').selectize();
#                         });
#                     })('django' in window && django.jQuery ? django.jQuery: jQuery);
#                 </script>''' % name
#         return  mark_safe("%s %s" % (html, js))


class ColorPickerWidget(TextInput):
    """Color Picker for html5 input type color, using bootstrap-colorpicker.js as fallback """
    input_type = 'color'
        
    def render(self, name, value, attrs=None):
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