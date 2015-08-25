from django.utils.translation import gettext as _

from django.forms import ModelForm, ValidationError
from django.forms.models import inlineformset_factory, modelform_factory

from django.forms.widgets import SplitDateTimeWidget

from myDmarcApp.models import Report, Reporter, ReportError, Record, \
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet, \
    TimeFixed, TimeVariable, ViewFilterField, ReportSender, ReportReceiverDomain, \
    SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult, \
    AlignedDkimResult, AlignedSpfResult, Disposition
from myDmarcApp.widgets import MultiSelectWidget, ColorPickerWidget




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
            self.time_fixed_form.add_error(None, ValidationError(_('Specify only one of both fields!'), code='double time error',))
            time_valid = False
        elif not self.time_variable_form.is_valid() and not self.time_fixed_form.is_valid():
            self.time_fixed_form.add_error(None, ValidationError(_('Specify at least one of both fields!'), code='double time error',))
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

ReportSenderFormSet                 = inlineformset_factory(FilterSet, ReportSender, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Report Sender'}, widgets={
                                    'value': MultiSelectWidget(choices=Reporter.objects.distinct().values_list('email', 'email'))})

ReportReceiverDomainFormSet         = inlineformset_factory(FilterSet, ReportReceiverDomain, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Report Receiver Domain'}, widgets={
                                    'value': MultiSelectWidget(choices=Report.objects.distinct().values_list('domain', 'domain'))})

SourceIPFormSet                     = inlineformset_factory(FilterSet, SourceIP, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Source IP'})

RawDkimDomainFormSet                = inlineformset_factory(FilterSet, RawDkimDomain, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Raw DKIM Domain'}, widgets={
                                    'value': MultiSelectWidget(choices=AuthResultDKIM.objects.distinct().values_list('domain', 'domain'))})

RawDkimResultFormSet                = inlineformset_factory(FilterSet, RawDkimResult, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Raw DKIM Result'}, widgets={'value': MultiSelectWidget})

RawSpfDomainFormSet                 = inlineformset_factory(FilterSet, RawSpfDomain, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Raw SPF Domain'}, widgets={
                                    'value': MultiSelectWidget(choices=AuthResultSPF.objects.distinct().values_list('domain', 'domain'))}
                                    )

RawSpfResultFormSet                 = inlineformset_factory(FilterSet, RawSpfResult, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Raw SPF Result'}, widgets={'value': MultiSelectWidget})

AlignedDkimResultFormSet            = inlineformset_factory(FilterSet, AlignedDkimResult, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Aligned DKIM Result'}, widgets={'value': MultiSelectWidget})


AlignedSpfResultFormSet             = inlineformset_factory(FilterSet, AlignedSpfResult, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Aligned SPF Result'}, widgets={'value': MultiSelectWidget})

DispositionFormSet                  = inlineformset_factory(FilterSet, Disposition, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Dispostion'}, widgets={'value': MultiSelectWidget})

FilterSetFormSet                    = inlineformset_factory(View, FilterSet, can_delete=True, extra=2,
                                    fields=('label', 'color'), widgets={'color': ColorPickerWidget})