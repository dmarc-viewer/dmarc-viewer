from django import template

register = template.Library()

@register.assignment_tag
def join_filter_set_field_values(filter_set_fields, get_display):
    joined_filter_set_fields = ""
    if filter_set_fields:
        if get_display:
            joined_filter_set_fields += " or ".join(["'{}'".format(field.get_value_display())
                    for field in filter_set_fields])
        else:
            joined_filter_set_fields += " or ".join(["'{}'".format(field.value)
                    for field in filter_set_fields])

    return joined_filter_set_fields


@register.assignment_tag
def get_filter_set_field_tuples(filter_set):
    return [
        ("Report Sender Email", filter_set.reportsender_set.all, False),
        ("Report Receiver Domain", filter_set.reportreceiverdomain_set.all, False),
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


@register.inclusion_tag('website/view-editor-filterset.html')
def show_filter_set(form):
    return {'form': form}
