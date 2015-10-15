from django import template

register = template.Library()

@register.simple_tag
def join_filter_set_field_values(filter_set_fields, name, join_string = ', ', get_display=False):
    output = ""
    if (filter_set_fields):
        output = name 
        if get_display:
            output += ": " + join_string.join([f.get_value_display() for f in filter_set_fields])
        else: 
            output += ": " + join_string.join([str(f.value) for f in filter_set_fields])

    return output


@register.inclusion_tag('myDmarcApp/view-editor-filterset.html')
def show_filter_set(form):
    return {'form': form}