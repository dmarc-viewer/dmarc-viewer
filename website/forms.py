"""
<Program Name>
    forms.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    July 22, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    TODO:
        - Purpose
        - class and function docstrings
        - comments

"""


from django.utils.translation import gettext as _
from django.forms import (ModelForm, ValidationError, ChoiceField,
        MultipleChoiceField, TypedMultipleChoiceField, CharField,
        GenericIPAddressField, IntegerField, DateTimeField, TypedChoiceField,
        BooleanField)
from django.forms.models import inlineformset_factory, modelform_factory
from django.forms.widgets import RadioSelect, Textarea
from website.models import (Report, Reporter, ReportError, Record,
        PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet,
        ReportType, DateRange, ReportSender, ReportReceiverDomain,
        SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult,
        AlignedDkimResult, AlignedSpfResult, Disposition, MultipleDkim)
from website.widgets import (ColorPickerWidget, MultiSelectWidget,
    DatePickerWidget)
from website import choices

class ViewForm(ModelForm):
    class Meta:
        model = View
        fields = ["title", "description", "enabled", "type_map", "type_line",
                "type_table"]
        labels = {
            "enabled": _("show in Deep Analysis"),
            "type_map": _("world map"),
            "type_line": _("time line chart"),
            "type_table": _("report record table"),
        }
        widgets = {
            "description": Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super(ViewForm, self).__init__(*args, **kwargs)
        self.fields["report_type"] = ChoiceField(label="Report Type",
                choices=choices.REPORT_TYPE, required=True)

        # Initialize all fields for date range
        self.fields["dr_type"] = TypedChoiceField(label="Report Date Range",
                choices=choices.DATE_RANGE_TYPE, coerce=int,
                widget=RadioSelect())
        self.fields["quantity"] = IntegerField(label="", min_value=1,
                required=False)
        self.fields["unit"] = TypedChoiceField(label="", coerce=int,
                choices=choices.TIME_UNIT, required=False)
        self.fields["begin"] = DateTimeField(label="", required=False,
                widget=DatePickerWidget())
        self.fields["end"] = DateTimeField(label="", required=False,
                widget=DatePickerWidget())

        # Set default for date range type
        self.fields["dr_type"].initial = choices.DATE_RANGE_TYPE_FIXED

        # If this form is already bound to a view, add the data from the model
        if self.instance.id:
            for date_range in DateRange.objects.filter(
                    foreign_key=self.instance.id):
                self.fields["dr_type"].initial = date_range.dr_type

                self.fields["unit"].initial = date_range.unit
                self.fields["quantity"].initial = date_range.quantity

                if date_range.begin:
                    self.fields["begin"].initial = date_range.begin.strftime(
                            "%Y-%m-%d")
                if date_range.end:
                    self.fields["end"].initial = date_range.end.strftime(
                            "%Y-%m-%d")

            for report_type in ReportType.objects.filter(
                    foreign_key=self.instance.id):
                self.fields["report_type"].initial = report_type.value

    def clean(self):
        cleaned_data = super(ViewForm, self).clean()
        dr_type = cleaned_data.get("dr_type")
        begin = cleaned_data.get("begin")
        end = cleaned_data.get("end")
        quantity = cleaned_data.get("quantity")
        unit = cleaned_data.get("unit")

        # Only one of both pairs (fixed or variable) should ever be specified
        only_one_msg = _("Specify either fixed or variable time range!")
        if (((dr_type == choices.DATE_RANGE_TYPE_FIXED) and
                (unit or quantity)) or
                ((dr_type == choices.DATE_RANGE_TYPE_VARIABLE) and
                (begin or end))):
            self.add_error("begin",
                    ValidationError(only_one_msg, code="required"))
            self.add_error("end",
                    ValidationError(only_one_msg, code="required"))
            self.add_error("unit",
                    ValidationError(only_one_msg, code="required"))
            self.add_error("quantity",
                    ValidationError(only_one_msg, code="required"))

        # If the user wants fixed ranges begin and end must be specified
        required_msg = _("This field is required.")
        if dr_type == choices.DATE_RANGE_TYPE_FIXED:
            if not begin:
                self.add_error("begin",
                        ValidationError(required_msg, code="required"))
            if not end:
                self.add_error("end",
                        ValidationError(required_msg, code="required"))

        # Ff the user wants variable ranges unit and quantity must be specified
        if dr_type == choices.DATE_RANGE_TYPE_VARIABLE:
            if not unit:
                self.add_error("unit",
                        ValidationError(required_msg, code="required"))
            if not quantity:
                self.add_error("quantity",
                        ValidationError(required_msg, code="required"))

        return cleaned_data

    def save(self):
        view_instance = super(ViewForm, self).save()

        # This is actually a one-to-one relationship but modeled with fk (m2o)
        date_range = DateRange.objects.filter(
                foreign_key=self.instance.id).first()

        if not date_range:
            date_range = DateRange(foreign_key=self.instance)

        date_range.dr_type = self.cleaned_data["dr_type"]
        date_range.unit = self.cleaned_data["unit"] or None
        date_range.quantity = self.cleaned_data["quantity"]
        date_range.begin = self.cleaned_data["begin"]
        date_range.end = self.cleaned_data["end"]

        date_range.save()

        # This is actually a one-to-one relationship but modeled with fk (m2o)
        report_type = ReportType.objects.filter(
                foreign_key=self.instance.id).first()
        if not report_type:
            report_type = ReportType(foreign_key=self.instance)
        report_type.value = self.cleaned_data["report_type"]
        report_type.save()

        return view_instance

class MyTypedMultipleChoiceField(TypedMultipleChoiceField):
    """A TypedMultipleChoiceField without real validation.
    Enables dynamic adding of choices on client side.
    We need this because we add some choices with ajax.
    """
    def validate(self, values):
        """Add new values to choices list. To show them again in client if
        view is invalid. """
        for value in values:
            for choice_tuple in self.choices:
                if value == choice_tuple[0]:
                    return True
            self.choices.append((value, value))
        return True


class FilterSetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FilterSetForm, self).__init__(*args, **kwargs)
        self.additional_filter_fields = {
            "report_sender" : {
                "load" : "reporter", # cf. view.py - choices_async
                "label" : "Reporter(s)",
                "class" : ReportSender,
                "type" : unicode
            },
            "report_receiver_domain" : {
                "load" : "reportee", # cf. view.py - choices_async
                "label" : "Reportee(s)",
                "class" : ReportReceiverDomain,
                "type" : unicode
            },
            "raw_dkim_domain" : {
                "load" : "dkim_domain", # cf. view.py - choices_async
                "label" : "DKIM Domain(s)",
                "class" : RawDkimDomain,
                "type" : unicode
            },
            "raw_spf_domain" : {
                "load" : "spf_domain", # cf. view.py - choices_async
                "label" : "SPF Domain(s)",
                "class" : RawSpfDomain,
                "type" : unicode},
            "raw_dkim_result" :  {
                "choices" : choices.DKIM_RESULT,
                "label" : "DKIM Result(s)",
                "class" : RawDkimResult,
                "type" : int
            },
            "raw_spf_result" : {
                "choices" : choices.SPF_RESULT,
                "label" : "SPF Result(s)",
                "class" : RawSpfResult,
                "type" : int
            },
            "aligned_dkim_result" : {
                "choices" : choices.DMARC_RESULT,
                "label" : "Aligned DKIM Result(s)",
                "class" : AlignedDkimResult,
                "type" : int
            },
            "aligned_spf_result" : {
                "choices" : choices.DMARC_RESULT,
                "label" : "Aligned SPF Result(s)",
                "class" : AlignedSpfResult,
                "type" : int
            },
            "disposition" : {
                "choices" : choices.DISPOSITION_TYPE,
                "label"   : "Disposition(s)",
                "class"   : Disposition,
                "type"    : int
            }
        }

        # Initialize additional multiple choice filter set fields.
        for field_name, field_dict in self.additional_filter_fields.iteritems():

            # Creating a typed choice field helps performing built in form clean magic
            self.fields[field_name] = MyTypedMultipleChoiceField(
                    coerce=field_dict.get("type"),
                    required=False,
                    label=field_dict.get("label"),
                    choices=field_dict.get("choices", ()),
                    widget=MultiSelectWidget(
                            **{
                                "load": field_dict.get("load", "")
                            }))

            # Add select options already stored to db
            if self.instance.id:
                self.fields[field_name].initial = field_dict["class"].\
                        objects.filter(foreign_key=self.instance.id).\
                        values_list("value", flat=True)

                if not field_dict.get("choices"):
                    self.fields[field_name].choices = \
                        [(value, value) \
                        for value in self.fields[field_name].initial]

        # These are extra because they are one-to-one ergo no MultipleChoiceField
        self.fields["source_ip"] = GenericIPAddressField(required=False,
                label="Mail Sender IP")
        self.fields["multiple_dkim"] = BooleanField(required=False,
                label="Multiple DKIM only")

        if self.instance.id:
            source_ip_initial = SourceIP.objects.filter(
                    foreign_key=self.instance.id).values_list(
                    "value", flat=True)

            if len(source_ip_initial):
                self.fields["source_ip"].initial = source_ip_initial[0]

            multiple_dkim_initial = MultipleDkim.objects.filter(
                    foreign_key=self.instance.id).values_list(
                    "value", flat=True)

            if len(multiple_dkim_initial):
                self.fields["multiple_dkim"].initial = multiple_dkim_initial[0]

    def save(self, commit=True):

        instance = super(FilterSetForm, self).save()

        # Add new many-to-one filter fields to a filter set object
        # remove existing if removed in form
        for field_name, field_dict in self.additional_filter_fields.iteritems():
            # Get list of existing filters
            existing_filters = list(field_dict["class"].objects.filter(
                    foreign_key=self.instance.id).values_list(
                    "value", flat=True))

            for filter_value in self.cleaned_data[field_name]:
                # Save new filters
                if filter_value not in existing_filters:
                    new_filter = field_dict["class"]()
                    new_filter.foreign_key = self.instance
                    new_filter.value = filter_value
                    new_filter.save()
                else:
                    existing_filters.remove(filter_value)
            # Delete old filters that were deleted in form
            for deleted_filter in existing_filters:
                field_dict["class"].objects.filter(
                        foreign_key=self.instance.id,
                        value=deleted_filter).delete()


        #  update, create or delete source_ip
        source_ip = SourceIP.objects.filter(
                foreign_key=self.instance.id).first()
        source_ip_value = self.cleaned_data["source_ip"]
        if source_ip and not source_ip_value:
            source_ip.delete()

        if not source_ip and source_ip_value:
            source_ip = SourceIP(
                    foreign_key=self.instance, value=source_ip_value)
            source_ip.save()

        if source_ip and source_ip_value:
            source_ip.value = source_ip_value
            source_ip.save()

        # delete or create multiple dkim only
        # we don"t have to update because we keep only true valued instances
        multiple_dkim = MultipleDkim.objects.filter(
                foreign_key=self.instance.id).first()
        multiple_dkim_value = self.cleaned_data["multiple_dkim"]

        if multiple_dkim and not multiple_dkim_value:
            multiple_dkim.delete()

        if not multiple_dkim and multiple_dkim_value:
            multiple_dkim = MultipleDkim(foreign_key=self.instance,
                    value=multiple_dkim_value)
            multiple_dkim.save()

        return instance

    class Meta:
        model = FilterSet
        fields = ["label", "color"]
        widgets = {"color": ColorPickerWidget}

FilterSetFormSet = inlineformset_factory(
        View, FilterSet, form=FilterSetForm, can_delete=True, extra=0)