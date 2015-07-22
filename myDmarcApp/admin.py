from django.contrib.gis import admin
from super_inlines.admin import SuperInlineModelAdmin, SuperModelAdmin
from myDmarcApp.models import Report, Reporter, ReportError, Record, \
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet, \
    TimeFixed, TimeVariable, ViewFilterField, ReportSender, ReportReceiverDomain, \
    SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult, \
    AlignedDkimResult, AlignedSpfResult, Disposition

class PolicyOverrideReasonInline(admin.StackedInline):
    model = PolicyOverrideReason
    extra = 0

class AuthResultSPFInline(SuperInlineModelAdmin, admin.StackedInline):
    model = AuthResultSPF
    extra = 0

class AuthResultDKIMInline(SuperInlineModelAdmin, admin.StackedInline):
    model = AuthResultDKIM
    extra = 0

class RecordInline(SuperInlineModelAdmin, admin.StackedInline):
    model = Record
    extra = 0
    inlines = (PolicyOverrideReasonInline, AuthResultSPFInline, AuthResultDKIMInline,)

class ReportErrorInline(SuperInlineModelAdmin, admin.StackedInline):
    model = ReportError
    extra = 0

class ReporterAdmin(SuperModelAdmin):
    model = Reporter 
    list_display = ('org_name', 'email', 'extra_contact_info')

class ReportAdmin(SuperModelAdmin):
    list_display = ('report_id', 'date_range_begin', 'date_range_end', 'report_type', 'date_created')
    inlines = (ReportErrorInline, RecordInline,)

admin.site.register(Report, ReportAdmin)
admin.site.register(Reporter, ReporterAdmin)


class ReportSenderInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = ReportSender
class ReportReceiverDomainInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = ReportReceiverDomain
class SourceIPInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = SourceIP
class RawDkimDomainInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = RawDkimDomain
class RawDkimResultInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = RawDkimResult
class RawSpfDomainInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = RawSpfDomain
class RawSpfResultInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = RawSpfResult
class AlignedDkimResultInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = AlignedDkimResult
class AlignedSpfResultInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = AlignedSpfResult
class DispositionInline(SuperInlineModelAdmin, admin.StackedInline):
    extra = 0
    model = Disposition

class FilterSetInline(SuperInlineModelAdmin, admin.StackedInline):
    model = FilterSet
    extra = 1
    inlines = (ReportSenderInline, ReportReceiverDomainInline,\
        SourceIPInline, RawDkimDomainInline, RawDkimResultInline,\
         RawSpfDomainInline, RawSpfResultInline, AlignedDkimResultInline,\
         AlignedSpfResultInline, DispositionInline,)

class TimeFixedInline(SuperInlineModelAdmin, admin.StackedInline):
    model = TimeFixed
    extra = 1

class TimeVariableInline(SuperInlineModelAdmin, admin.StackedInline):
    model = TimeVariable
    extra = 1

class ViewAdmin(SuperModelAdmin):
    inlines = (TimeFixedInline, TimeVariableInline, FilterSetInline,)

admin.site.register(View, ViewAdmin)