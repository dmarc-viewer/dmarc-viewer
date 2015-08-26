from django.utils.translation import gettext as _

from django.forms import ModelForm, ValidationError, MultipleChoiceField, CharField, IPAddressField
from django.forms.models import inlineformset_factory, modelform_factory

from django.forms.widgets import SplitDateTimeWidget

from myDmarcApp.models import Report, Reporter, ReportError, Record, \
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet, \
    TimeFixed, TimeVariable, ViewFilterField, ReportSender, ReportReceiverDomain, \
    SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult, \
    AlignedDkimResult, AlignedSpfResult, Disposition
from myDmarcApp.widgets import MultiSelectWidget, ColorPickerWidget
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
    report_sender = CharField(initial=Reporter.objects.distinct().values_list('id', 'email'), label='Report Sender', widget=MultiSelectWidget(attrs={'placeholder' : 'Report Sender'}, choices=Reporter.objects.distinct().values_list('id', 'email')))
    # report_receiver_domain = CharField(label='Report Receiver Domain', widget=MultiSelectWidget(attrs={'placeholder' : 'Report Receiver Domain'}, choices=Report.objects.distinct().values_list('domain', 'domain')))
    
    # source_ip = IPAddressField(label='Source IP')
    
    # raw_dkim_domain = CharField(label='Raw DKIM Domain', widget=MultiSelectWidget(attrs={'placeholder' : 'Raw DKIM Domain'}, choices=AuthResultDKIM.objects.distinct().values_list('domain', 'domain')))
    # raw_spf_domain = CharField(label='Raw SPF Domain', widget=MultiSelectWidget(attrs={'placeholder' : 'Raw SPF Domain'}, choices=AuthResultSPF.objects.distinct().values_list('domain', 'domain')))
    
    # raw_dkim_result = CharField(label='Raw DKIM Result', widget=MultiSelectWidget(attrs={'placeholder' : 'Raw DKIM Result'}, choices=choices.DKIM_RESULT))
    # raw_spf_result = CharField(label='Raw SPF Result', widget=MultiSelectWidget(attrs={'placeholder' : 'Raw SPF Result'}, choices=choices.SPF_RESULT))

    # aligned_dkim_result = CharField(label='Aligned DKIM Result', widget=MultiSelectWidget(attrs={'placeholder' : 'Aligned DKIM Result'}, choices=choices.DMARC_RESULT))
    # aligned_spf_result = CharField(label='Aligned SPF Result', widget=MultiSelectWidget(attrs={'placeholder' : 'Aligned SPF Result'}, choices=choices.DMARC_RESULT))

    # disposition = CharField(label='Disposition', widget=MultiSelectWidget(attrs={'placeholder' : 'Disposition'}, choices=choices.DISPOSITION_TYPE))

    def save(self):
        print self.report_sender

    class Meta:
        model = FilterSet
        fields = ['label', 'color']
        widgets = {'color': ColorPickerWidget}

FilterSetFormSet                    = inlineformset_factory(View, FilterSet, form=FilterSetForm, can_delete=True, extra=0)