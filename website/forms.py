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
    Configure analysis view model forms and form fields for the view editor.

    See https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/ for
    more information on creating forms from models.

    This module defines custom `ModelForm` subclasses for `View` and
    `FilterSet` objects and extends constructor, and `clean` and `save` methods
    to make use of Django's awesome form magic, like creating HTML form fields
    from model fields, or input validation/sanitization.

"""
from django.utils.translation import gettext as _
from django.forms import (ModelForm, ValidationError, ChoiceField,
        MultipleChoiceField, TypedMultipleChoiceField, CharField,
        GenericIPAddressField, IntegerField, DateTimeField, TypedChoiceField,
        BooleanField)
from django.forms.models import inlineformset_factory, modelform_factory
from django.forms.widgets import RadioSelect, Textarea
from django.urls import reverse

from website.models import (Report, Reporter, ReportError, Record,
        PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet,
        ReportType, DateRange, ReportSender, ReportReceiverDomain,
        SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult,
        AlignedDkimResult, AlignedSpfResult, Disposition, MultipleDkim)
from website.widgets import (ColorPickerWidget, MultiSelectWidget,
        DatePickerWidget)
from website import choices




class ViewForm(ModelForm):
    """ModelForm used to manage creating and editing of `View` objects using
    HTML web forms.
    See https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/
    """


    class Meta:
        """Use Meta class to configure default form fields for `View`
        attributes. """
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
        """Custom model form constructor to account for custom related objects,
        i.e. instances of (subclasses of) `ViewFilterField`. """
        super(ViewForm, self).__init__(*args, **kwargs)

        # Initialize form field for related `ReportType` object
        self.fields["report_type"] = ChoiceField(label="Report Type",
                choices=choices.REPORT_TYPE, required=True)

        # Initialize form fields for related `DateRange` object, assigning
        # custom date picker widgets
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

        # Set default form value for `DateRange`'s date range type field
        self.fields["dr_type"].initial = choices.DATE_RANGE_TYPE_FIXED

        # Fill form with existing `ViewFilterField` data if any. Unbound forms,
        # i.e. forms without data, don't have an instance id.
        if self.instance.id:
            # Note, there can at most be one `DateRange` and one `ReportType`
            # object on a view. See `models.ViewFilterField`'s docstring for
            # more info.
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
        """Custom model form validation/sanitization method, to account for
        custom related objects, i.e. instances of (subclasses of)
        `ViewFilterField`. """
        cleaned_data = super(ViewForm, self).clean()

        # Fetch pre-sanitized `DateRange` data and perform custom validation
        dr_type = cleaned_data.get("dr_type")
        begin = cleaned_data.get("begin")
        end = cleaned_data.get("end")
        quantity = cleaned_data.get("quantity")
        unit = cleaned_data.get("unit")

        # 1) Validate exclusiveness
        # `DateRange` objects can carry either a fixed (i.e. "from to begin"),
        # or a dynamic (i.e. "last <n> days/etc.") date range, but not both.
        only_one_msg = _("Specify either fixed or variable time range!")
        if ((dr_type == choices.DATE_RANGE_TYPE_FIXED and
                (unit or quantity)) or
                (dr_type == choices.DATE_RANGE_TYPE_VARIABLE and
                (begin or end))):
            self.add_error("begin",
                    ValidationError(only_one_msg, code="required"))
            self.add_error("end",
                    ValidationError(only_one_msg, code="required"))
            self.add_error("unit",
                    ValidationError(only_one_msg, code="required"))
            self.add_error("quantity",
                    ValidationError(only_one_msg, code="required"))

        # 2a) Validate fixed date range
        required_msg = _("This field is required.")
        if dr_type == choices.DATE_RANGE_TYPE_FIXED:
            if not begin:
                self.add_error("begin",
                        ValidationError(required_msg, code="required"))
            if not end:
                self.add_error("end",
                        ValidationError(required_msg, code="required"))

        # 2b) Validate custom date range
        if dr_type == choices.DATE_RANGE_TYPE_VARIABLE:
            if not unit:
                self.add_error("unit",
                        ValidationError(required_msg, code="required"))
            if not quantity:
                self.add_error("quantity",
                        ValidationError(required_msg, code="required"))

        return cleaned_data


    def save(self):
        """Custom model form create/update method, to account for custom
        related objects, i.e. instances of (subclasses of) `ViewFilterField`.
        This method is called after `clean`.
        """
        view_instance = super(ViewForm, self).save()

        # There can at most be one `DateRange` object on a view. See
        # `models.ViewFilterField`'s docstring for more info.
        date_range = DateRange.objects.filter(
                foreign_key=self.instance.id).first()

        # Create if does not exist
        if not date_range:
            date_range = DateRange(foreign_key=self.instance)

        # Assign values
        date_range.dr_type = self.cleaned_data["dr_type"]
        date_range.unit = self.cleaned_data["unit"] or None
        date_range.quantity = self.cleaned_data["quantity"]
        date_range.begin = self.cleaned_data["begin"]
        date_range.end = self.cleaned_data["end"]

        # Persist in DB
        date_range.save()

        # There can at most be one `ReportType` object on a view. See
        # `models.ViewFilterField`'s docstring for more info.
        report_type = ReportType.objects.filter(
                foreign_key=self.instance.id).first()

        # Create if does not exist
        if not report_type:
            report_type = ReportType(foreign_key=self.instance)
        report_type.value = self.cleaned_data["report_type"]

        # Persist in DB
        report_type.save()

        return view_instance



class AsyncTypedMultipleChoiceField(TypedMultipleChoiceField):
    """Custom `TypedMultipleChoiceField` used for multiselect form fields whose
    options are retrieved dynamically so that already selected fields are
    available on the client in forms, whose validation failed for some other
    reason. Using a "typed" choice field helps performing built-in Django form
    clean magic.
    """


    def validate(self, values):
        """Add selected options (`values`) to list of options (`choices`) to
        make them available in the form that is presented to the user to fix
        (other) invalid fields. This method is called by the corresponding
        field's `clean` method.
        """
        for value in values:
            for choice_tuple in self.choices:
                if value == choice_tuple[0]:
                    return True
            self.choices.append((value, value))
        return True



class FilterSetForm(ModelForm):
    """ModelForm used to manage creating and editing of `FilteSet` objects
    using HTML web forms.
    See https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/
    """


    class Meta:
        """Use Meta class to configure default form fields for `FilterSet`
        attributes. """
        model = FilterSet
        fields = ["label", "color"]
        widgets = {"color": ColorPickerWidget}


    def __init__(self, *args, **kwargs):
        """Custom model form constructor to account for custom related objects,
        i.e. instances of (subclasses of) `FilterSetFilterField`. """
        super(FilterSetForm, self).__init__(*args, **kwargs)

        # Define all filter set filter fields for which we want form fields
        # The "choice" field contains the list of available options.
        # Multiselect form fields that load their choices asynchronously define
        # a "load" value, used to identify the DMARC aggregate report field
        # from which the options should be loaded.
        # See `views.choices_async` and `widgets.MultiSelectWidget`
        # The "label" value is used as text for the corresponding HTML label
        # element, "class" identifies the corresponding model class (subclass
        # of `FilterSetFilterField`), and "type" defines the allowed type of
        # the form value, used for Django's auto sanitization/type coercion.
        self.multiselect_filter_fields = {
            "report_sender" : {
                "load" : "reporter",
                "label" : "Reporter(s)",
                "class" : ReportSender,
                "type" : unicode
            },
            "report_receiver_domain" : {
                "load" : "reportee",
                "label" : "Reportee(s)",
                "class" : ReportReceiverDomain,
                "type" : unicode
            },
            "raw_dkim_domain" : {
                "load" : "dkim_domain",
                "label" : "DKIM Domain(s)",
                "class" : RawDkimDomain,
                "type" : unicode
            },
            "raw_spf_domain" : {
                "load" : "spf_domain",
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

        # Initialize `FilterSetFilterField` form fields from dict defined above
        # The keyword arguments passed to the `MultiSelectWidget` constructor
        # are only relevant for multiselect elements that load their options
        # dynamically.
        for field_name, field_dict in self.multiselect_filter_fields.iteritems():
            self.fields[field_name] = AsyncTypedMultipleChoiceField(
                    coerce=field_dict.get("type"),
                    required=False,
                    label=field_dict.get("label"),
                    choices=field_dict.get("choices", ()),
                    widget=MultiSelectWidget(
                            **{
                                "load": field_dict.get("load", ""),
                                "action": reverse("choices_async")
                            }))

            # If the corresponding model objects already exists (i.e. on edit)
            # the selected options should also be shown as selected in the form
            if self.instance.id:
                self.fields[field_name].initial = list(
                        field_dict["class"].objects.filter(
                        foreign_key=self.instance.id).values_list(
                        "value", flat=True))

                # For multiselect fields that load their options asynchronously
                # we have to add already selected options to the field's
                # choices attribute
                if not field_dict.get("choices"):
                    self.fields[field_name].choices = [(value, value)
                            for value in self.fields[field_name].initial]


        # Define additional non-multiselect filter set filter field form fields
        # Currently, there can at most be one `SourceIP` and one `MultipleDkim`
        # object on a filter set. See `models.FilterSetFilterField`'s docstring
        # for more info about why these filters have their own class and aren't
        # attributes of a `FilterSet` object.
        self.fields["source_ip"] = GenericIPAddressField(required=False,
                label="Mail Sender IP")
        self.fields["multiple_dkim"] = BooleanField(required=False,
                label="Multiple DKIM only")

        # Fill fields with existing data if any
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
        """Custom model form create/update method, to account for custom
        related objects, i.e. instances of (subclasses of)
        `FilterSetFilterField`.
        """
        instance = super(FilterSetForm, self).save()

        # Create or delete subclasses of `FilterSetFilterField` corresponding
        # to a given multiselect form field.
        for field_name, field_dict in self.multiselect_filter_fields.iteritems():
            # Get existing filter values
            existing_filters = list(field_dict["class"].objects.filter(
                    foreign_key=self.instance.id).values_list(
                    "value", flat=True))

            # Iterate over posted filter values
            for filter_value in self.cleaned_data[field_name]:
                # Create new object if posted value does not exist yet
                if filter_value not in existing_filters:
                    new_filter = field_dict["class"]()
                    new_filter.foreign_key = self.instance
                    new_filter.value = filter_value
                    new_filter.save()

                # Remove from list of existing filters otherwise
                # Remaining existing filters will be deleted below
                else:
                    existing_filters.remove(filter_value)

            # Delete remaining objects whose corresponding value was not
            # posted, i.e. deleted on the client side
            for deleted_filter in existing_filters:
                field_dict["class"].objects.filter(
                        foreign_key=self.instance.id,
                        value=deleted_filter
                        ).delete()


        # Create, update or delete corresponding `SourceIP` object
        # Currently, there can at most be one `SourceIP` object on a filter
        # set. See `models.FilterSetFilterField`'s docstring for more info.
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

        # Delete or create corresponding `MultipleDkim` object
        # There is no need to update because we only keep true valued
        # instances. There can at most be one `MultipleDkim` object on a filter
        # set. See `models.FilterSetFilterField`'s docstring for more info.
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



# Create an inline formset to be used in the `edit` view
# https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/#inline-formsets
FilterSetFormSet = inlineformset_factory(
        View, FilterSet, form=FilterSetForm, can_delete=True, extra=0)