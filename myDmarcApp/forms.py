from django.forms import ModelForm
from myDmarcApp.models import Report, Reporter, ReportError, Record, \
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet, \
    TimeFixed, TimeVariable, ViewFilterField, ReportSender, ReportReceiverDomain, \
    SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult, \
    AlignedDkimResult, AlignedSpfResult, Disposition
from django.forms.models import inlineformset_factory, modelform_factory



TimeVariableFormSet = inlineformset_factory(View, TimeVariable, can_delete=False, extra=1,
                                    fields=('unit','quantity'))
TimeFixedFormSet    = inlineformset_factory(View, TimeFixed, can_delete=False, extra=1,
                                    fields=('date_range_begin', 'date_range_end'))

ViewForm            = modelform_factory(View, fields=('title', 'description', 'enabled', 'report_type'))

