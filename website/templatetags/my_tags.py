"""
<Program Name>
    my_tags.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    October, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Define custom Django template tags, i.e. regular Python functions that can
    be called from within Django templates.
    See https://docs.djangoproject.com/en/1.11/howto/custom-template-tags/

"""
from django import template
register = template.Library()



@register.assignment_tag
def join_filter_set_field_values(filter_set_fields, get_display):
    """Join passed `FilterSetFilter` objects' (display) values using the string
    ' or ' and return the resulting string. """
    joined_filter_set_fields = ""
    if filter_set_fields:
        if get_display:
            joined_filter_set_fields += " or ".join(
                    ["'{}'".format(field.get_value_display())
                    for field in filter_set_fields])
        else:
            joined_filter_set_fields += " or ".join(
                    ["'{}'".format(field.value)
                    for field in filter_set_fields])

    return joined_filter_set_fields


@register.assignment_tag
def get_filter_set_field_tuples(filter_set):
    """Return a list of tuples of filter set filter names and values.
    This is used together with above `join_filter_set_field_values` to create
    a table of filters used in an analysis view.

    NOTE:
     - This function and `join_filter_set_field_values` are kept separate so
       that we don't have to write HTML markup here.
       See `templates/website/view-editor-filterset.html`

     - It might be less of a hassle to prepare the data in the corresponding
       view, i.e. `website.views.deep_analysis`.

    """
    return [
        ("Report Sender Email", filter_set.reportsender_set.all, False),
        ("Report Receiver Domain", filter_set.reportreceiverdomain_set.all,
                False),
        ("Mail Sender Source IP", filter_set.sourceip_set.all, False),
        ("Aligned DKIM Result", filter_set.aligneddkimresult_set.all, True),
        ("Aligend SPF Result", filter_set.alignedspfresult_set.all, True),
        ("Disposition", filter_set.disposition_set.all, True),
        ("Raw SPF Domain", filter_set.rawspfdomain_set.all, False),
        ("Raw SPF Result", filter_set.rawspfresult_set.all, True),
        ("Raw DKIM Domain", filter_set.rawdkimdomain_set.all, False),
        ("Raw DKIM Result", filter_set.rawdkimresult_set.all, True),
        ("Multiple DKIM Only", filter_set.multipledkim_set.all, False),
    ]
