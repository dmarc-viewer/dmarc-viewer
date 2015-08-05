from django.forms import ModelForm
from django.forms.models import inlineformset_factory, modelform_factory

from django.forms.widgets import SplitDateTimeWidget
from colorful.widgets import ColorFieldWidget

from myDmarcApp.models import Report, Reporter, ReportError, Record, \
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet, \
    TimeFixed, TimeVariable, ViewFilterField, ReportSender, ReportReceiverDomain, \
    SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult, \
    AlignedDkimResult, AlignedSpfResult, Disposition
from myDmarcApp.widgets import MultiSelectWidget



TimeVariableFormSet                 = inlineformset_factory(View, TimeVariable, can_delete=False, extra=1,
                                    fields=('unit','quantity'))
TimeFixedFormSet                    = inlineformset_factory(View, TimeFixed, can_delete=False, extra=1,
                                    fields=('date_range_begin', 'date_range_end'))
ViewForm                            = modelform_factory(View, fields=('title', 'description', 'enabled', 'report_type'))

ReportSenderFormSet                 = inlineformset_factory(FilterSet, ReportSender, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Report Sender'}, widgets={'value': MultiSelectWidget})


ReportReceiverDomainFormSet         = inlineformset_factory(FilterSet, ReportReceiverDomain, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Report Receiver Domain'})
SourceIPFormSet                     = inlineformset_factory(FilterSet, SourceIP, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Source IP'})
RawDkimDomainFormSet                = inlineformset_factory(FilterSet, RawDkimDomain, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Raw DKIM Domain'})
RawDkimResultFormSet                = inlineformset_factory(FilterSet, RawDkimResult, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Raw DKIM Result'})
RawSpfDomainFormSet                 = inlineformset_factory(FilterSet, RawSpfDomain, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Raw SPF Domain'})
RawSpfResultFormSet                 = inlineformset_factory(FilterSet, RawSpfResult, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Raw SPF Result'})
AlignedDkimResultFormSet            = inlineformset_factory(FilterSet, AlignedDkimResult, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Aligned DKIM Result'})
AlignedSpfResultFormSet             = inlineformset_factory(FilterSet, AlignedSpfResult, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Aligned SPF Result'})
DispositionFormSet                  = inlineformset_factory(FilterSet, Disposition, can_delete=False, extra=2,
                                    fields=('value',), labels={'value' : 'Dispostion'})
FilterSetFormSet                    = inlineformset_factory(View, FilterSet, can_delete=False, extra=2,
                                    fields=('label', 'color'), widgets={'color': ColorFieldWidget})