from django.contrib import admin
from super_inlines.admin import SuperInlineModelAdmin, SuperModelAdmin
from myDmarcApp.models import Report, Reporter, ReportError, Record, PolicyOverrideReason, AuthResultDKIM, AuthResultSPF

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
