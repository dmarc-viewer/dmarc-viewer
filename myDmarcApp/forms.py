from django.utils.translation import gettext as _

from django.forms import ModelForm, ValidationError, ChoiceField, MultipleChoiceField, TypedMultipleChoiceField, CharField, GenericIPAddressField, IntegerField, DateTimeField, TypedChoiceField
from django.forms.models import inlineformset_factory, modelform_factory

from django.forms.widgets import SplitDateTimeWidget

from myDmarcApp.models import Report, Reporter, ReportError, Record, \
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet, ReportType, \
    TimeFixed, TimeVariable, ReportSender, ReportReceiverDomain, \
    SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult, \
    AlignedDkimResult, AlignedSpfResult, Disposition
from myDmarcApp.widgets import ColorPickerWidget, MultiSelectWidget
import choices

class ViewForm(ModelForm):

    class Meta:
        model = View
        fields = ['title', 'description', 'enabled']

    def __init__(self, *args, **kwargs):
        super(ViewForm, self).__init__(*args, **kwargs)
        self.fields["report_type"]              = ChoiceField(label="Report Type", choices=choices.REPORT_TYPE, required=True)
        self.fields["time_variable_quantity"]   = IntegerField(label="Report Date Range Unit", required=False)
        self.fields["time_variable_unit"]       = TypedChoiceField(label="Report Date Range Quantity", coerce=int, choices=choices.TIME_UNIT, required=False)
        self.fields["time_fixed_begin"]         = DateTimeField(label="Report Date Begin", required=False)
        self.fields["time_fixed_end"]           = DateTimeField(label="Report Date End", required=False)

        if self.instance.id:
            for time_fixed in TimeFixed.objects.filter(foreign_key=self.instance.id):
                self.fields["time_fixed_begin"].initial       = time_fixed.date_range_begin
                self.fields["time_fixed_end"].initial         = time_fixed.date_range_end

            for time_variable in TimeVariable.objects.filter(foreign_key=self.instance.id):
                self.fields["time_variable_unit"].initial     = time_variable.unit
                self.fields["time_variable_quantity"].initial = time_variable.quantity

            for report_type in ReportType.objects.filter(foreign_key=self.instance.id):
                self.fields["report_type"].initial            = report_type.value


    # def is_valid(self):
    #     view_valid = super(ViewForm, self).is_valid()

    #     if ("time_variable_unit" in self.cleaned_data and "time_variable_quantity" in self.cleaned_data) \
    #      == ("time_fixed_begin" in self.cleaned_data and "time_fixed_end" in self.cleaned_data):
    #         self.add_error(None, ValidationError(_('Specify only one of both time fields!'), code='double time error',))
    #         time_valid = False

    #     elif not (("time_variable_unit" in self.cleaned_data and "time_variable_quantity" in self.cleaned_data) \
    #      or ("time_fixed_begin" in self.cleaned_data and "time_fixed_end" in self.cleaned_data)):
    #         self.time_fixed_form.add_error(None, ValidationError(_('Specify at least one of both!'), code='double time error',))
    #         time_valid = False
    #     else:
    #         time_valid = True

    #     return view_valid and time_valid

    def save(self):
        view_instance = super(ViewForm, self).save()
        
        # This is actually a one-to-one relationship but modeled with fk (m2o)
        time_variable = TimeVariable.objects.filter(foreign_key=self.instance.id).first()
        if self.cleaned_data["time_variable_unit"] and self.cleaned_data["time_variable_quantity"]:
            # Create or update 
            if not time_variable:
                time_variable = TimeVariable(foreign_key=self.instance)
            time_variable.unit          = self.cleaned_data["time_variable_unit"]
            time_variable.quantity      = self.cleaned_data["time_variable_quantity"]
            time_variable.save()
        else:
            # No data -> delete object if exists
            if time_variable:
                time_variable.delete()

        # This is actually a one-to-one relationship but modeled with fk (m2o)
        time_fixed = TimeFixed.objects.filter(foreign_key=self.instance.id).first()
        # Delete it if it was deleted in form 
        if self.cleaned_data["time_fixed_begin"] and self.cleaned_data["time_fixed_end"]:
            if not time_fixed:
                time_fixed = TimeFixed(foreign_key=self.instance)
            time_fixed.date_range_begin = self.cleaned_data["time_fixed_begin"]
            time_fixed.date_range_end   = self.cleaned_data["time_fixed_end"]
            time_fixed.save()
        else:
            if time_fixed:
                time_fixed.delete()

        # This is actually a one-to-one relationship but modeled with fk (m2o)
        report_type = ReportType.objects.filter(foreign_key=self.instance.id).first()
        if self.cleaned_data["report_type"]:
            if not report_type:
                report_type = ReportType(foreign_key=self.instance)
            report_type.value = self.cleaned_data["report_type"]
            report_type.save()

        return view_instance


class FilterSetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FilterSetForm, self).__init__(*args, **kwargs)
        self.additional_filter_fields = {
            "report_sender"              : {"choices" : Reporter.objects.distinct().values_list('email', 'email'), 
                                            "label"   : "Report Sender", 
                                            "class"   : ReportSender,
                                            "type"    : unicode},
            "report_receiver_domain"     : {"choices" : Report.objects.distinct().values_list('domain', 'domain'), 
                                            "label"   : "Report Receiver Domain", 
                                            "class"   : ReportReceiverDomain,
                                            "type"    : unicode},
            "raw_dkim_domain"            : {"choices" : AuthResultDKIM.objects.distinct().values_list('domain', 'domain'), 
                                            "label"   : "Raw DKIM Domain", 
                                            "class"   : RawDkimDomain,
                                            "type"    : unicode},
            "raw_spf_domain"             : {"choices" : AuthResultSPF.objects.distinct().values_list('domain', 'domain'), 
                                            "label"   : "Raw SPF Domain", 
                                            "class"   : RawSpfDomain,
                                            "type"    : unicode},
            "raw_dkim_result"            :  {"choices" : choices.DKIM_RESULT, 
                                            "label"   : "Raw DKIM Result", 
                                            "class"   : RawDkimResult,
                                            "type"    : int},
            "raw_spf_result"             : {"choices" : choices.SPF_RESULT, 
                                            "label"   : "Raw SPF Result", 
                                            "class"   : RawSpfResult,
                                            "type"    : int},
            "aligned_dkim_result"        : {"choices" : choices.DMARC_RESULT, 
                                            "label"   : "Aligned DKIM Result", 
                                            "class"   : AlignedDkimResult,
                                            "type"    : int},
            "aligned_spf_result"         : {"choices" : choices.DMARC_RESULT, 
                                            "label"   : "Aligned SPF Result", 
                                            "class"   : AlignedSpfResult,
                                            "type"    : int},
            "disposition"                : {"choices" : choices.DISPOSITION_TYPE, 
                                            "label"   : "Disposition", 
                                            "class"   : Disposition,
                                            "type"    : int}
            }
        # Initialize additional multiple choice filter set fields.
        for field_name, field_dict in self.additional_filter_fields.iteritems():

            # Creating a typed choice field helps performing built in form clean magic
            self.fields[field_name]  = TypedMultipleChoiceField(coerce=field_dict["type"], required=False, label=field_dict["label"], choices=field_dict["choices"], widget=MultiSelectWidget)
            if self.instance.id:
                self.fields[field_name].initial = field_dict["class"].objects.filter(foreign_key=self.instance.id).values_list('value', flat=True)

         # This is extra because its one-to-one ergo no MultipleChoiceField
        self.fields["source_ip"] =  GenericIPAddressField(required=False, label='Source IP')
        if self.instance.id:
            source_ip_initial = SourceIP.objects.filter(foreign_key=self.instance.id).values_list('value', flat=True)
            if len(source_ip_initial):
                self.fields['source_ip'].initial = source_ip_initial[0]

    def save(self, commit=True):
        instance = super(FilterSetForm, self).save()

        # Add new many-to-one filter fields to a filter set object
        # remove existing if removed in form 
        for field_name, field_dict in self.additional_filter_fields.iteritems():
            existing_filters = field_dict["class"].objects.filter(foreign_key=self.instance.id).values_list('value', flat=True)
            for filter_value in field_dict["choices"]:
                # We need the first choices tuple, because this is stored in the db and refers to form values (cleaned data)
                filter_value = filter_value[0]
                if filter_value not in existing_filters and filter_value in self.cleaned_data[field_name]:
                    new_filter = field_dict["class"]()
                    new_filter.foreign_key = self.instance
                    new_filter.value = filter_value
                    new_filter.save()
                if filter_value in existing_filters and filter_value not in self.cleaned_data[field_name]:
                    field_dict["class"].objects.filter(foreign_key=self.instance.id, value=filter_value).delete()

        # get or create source_ip
        source_ip       = SourceIP.objects.filter(foreign_key=self.instance.id).first()
        source_ip_value = self.cleaned_data["source_ip"]
        if source_ip and not source_ip_value:
            source_ip.delete()

        if not source_ip and source_ip_value:
            source_ip = SourceIP(foreign_key=self.instance, value = source_ip_value)
            source_ip.save()

        if source_ip and source_ip_value:
            source_ip.value = source_ip_value
            source_ip.save()

        return instance

    class Meta:
        model = FilterSet
        fields = ['label', 'color']
        widgets = {'color': ColorPickerWidget}

FilterSetFormSet                    = inlineformset_factory(View, FilterSet, form=FilterSetForm, can_delete=True, extra=0)