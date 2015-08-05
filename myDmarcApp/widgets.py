from django import forms
from django.forms.widgets import SelectMultiple
from django.utils.safestring import mark_safe

class MultiSelectWidget(SelectMultiple):
    """Simple Multi Select using Selectize.js"""

    def __init__(self, attrs=None, choices=()):
        super(MultiSelectWidget, self).__init__(attrs)
        self.choices = list((('1', 'First',), ('2', 'Second',)))

    class Media:
        css = {
            'all': ("selectize/css/selectize.css", "selectize/css/selectize.default.css", 
                "selectize/css/selectize.legacy.css", "selectize/css/selectize.bootstrap3.css",)
        }
        js = ("selectize/js/standalone/selectize.min.js",)
        
        
    def render(self, name, value, attrs=None):
        html = super(MultiSelectWidget, self).render(name, value, attrs)
        js   =  '''<script type="text/javascript">
                    (function($){
                        $(document).ready(function(){
                            $('#id_%s').selectize();
                        });
                    })('django' in window && django.jQuery ? django.jQuery: jQuery);
                </script>''' % name
        return  mark_safe("%s %s" % (html, js))