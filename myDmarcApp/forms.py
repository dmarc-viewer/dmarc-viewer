from django.utils.translation import gettext as _

from django.forms import ModelForm, ValidationError, MultipleChoiceField, TypedMultipleChoiceField, CharField, GenericIPAddressField
from django.forms.models import inlineformset_factory, modelform_factory

from django.forms.widgets import SplitDateTimeWidget

from myDmarcApp.models import Report, Reporter, ReportError, Record, \
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet, \
    TimeFixed, TimeVariable, ViewFilterField, ReportSender, ReportReceiverDomain, \
    SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult, \
    AlignedDkimResult, AlignedSpfResult, Disposition
from myDmarcApp.widgets import ColorPickerWidget, MultiSelectWidget
import choices


TimeVariableForm                    = modelform_factory(TimeVariable, fields=('unit','quantity'))
TimeFixedForm                       = modelform_factory(TimeFixed, fields=('date_range_begin', 'date_range_end'))

class ViewForm(ModelForm):
    class Meta:
        model = View
        fields = ['title', 'description', 'enabled', 'report_type']

    def __init__(self, *args, **kwargs):
        self.time_variable_form = kwargs.pop('time_variabe_form')
        self.time_fixed_form = kwargs.pop('time_fixed_form')
        super(ViewForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        view_valid = super(ViewForm, self).is_valid()
        if self.time_variable_form.is_valid() == self.time_fixed_form.is_valid():
            self.time_fixed_form.add_error(None, ValidationError(_('Specify only one of both!'), code='double time error',))
            time_valid = False
        elif not self.time_variable_form.is_valid() and not self.time_fixed_form.is_valid():
            self.time_fixed_form.add_error(None, ValidationError(_('Specify at least one of both!'), code='double time error',))
            time_valid = False
        else:
            time_valid = True

        return view_valid and time_valid

    def save(self):

        view_instance = super(ViewForm, self).save()
        
        if self.time_variable_form.is_valid():
            view_time_variable_instance = self.time_variable_form.save(commit=False)
            view_time_variable_instance.foreign_key = view_instance
            if self.time_fixed_form.instance.id:
                self.time_fixed_form.instance.delete()
            view_time_variable_instance.save()

        if self.time_fixed_form.is_valid():
            view_time_fixed_instance = self.time_fixed_form.save(commit=False)
            view_time_fixed_instance.foreign_key = view_instance
            if self.time_variable_form.instance.id:
                self.time_variable_form.instance.delete()
            view_time_fixed_instance.save()

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
        print self.instance.view_id
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