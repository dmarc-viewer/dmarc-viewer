from django.db import models
import choices

class Reporter(models.Model):
    org_name                = models.CharField(max_length = 100)
    email                   = models.EmailField()
    extra_contact_info      = models.CharField(max_length = 200)

    def __unicode__(self):
        return self.org_name

class Report(models.Model):
    """In the Schema a report is called feedback"""
    # Custom field to easily differ between incoming and outgoing
    report_type             = models.IntegerField(choices = choices.REPORT_TYPE)
    date_created            = models.DateTimeField(auto_now = False, auto_now_add = True)
    
    # Meta Data 
    report_id               = models.CharField(max_length = 200, unique = True)
    date_range_begin        = models.DateTimeField()
    date_range_end          = models.DateTimeField()

    version                 = models.DecimalField(max_digits = 4, decimal_places = 2, null = True)
    reporter                = models.ForeignKey('Reporter')

    # Policy Published
    domain                  = models.CharField(max_length = 100)
    adkim                   = models.IntegerField(choices = choices.ALIGNMENT_MODE, null = True)
    aspf                    = models.IntegerField(choices = choices.ALIGNMENT_MODE, null = True)
    p                       = models.IntegerField(choices = choices.DISPOSITION_TYPE)
    sp                      = models.IntegerField(choices = choices.DISPOSITION_TYPE, null = True)
    pct                     = models.IntegerField(null = True)
    fo                      = models.CharField(max_length = 8, null = True)

class ReportError(models.Model):
    report                  = models.ForeignKey('Report')
    error                   = models.CharField(max_length = 200)


class Record(models.Model):
    report                  = models.ForeignKey('Report')

    # Row
    source_ip               = models.GenericIPAddressField()
    #source_ip_location     =
    count                   = models.IntegerField()

    # Policy Evaluated
    disposition             = models.IntegerField(choices = choices.DISPOSITION_TYPE)
    dkim                    = models.IntegerField(choices = choices.DMARC_RESULT)
    spf                     = models.IntegerField(choices = choices.DMARC_RESULT)

    # Identifiers
    envelope_to             = models.CharField(max_length = 100, null = True)
    envelope_from           = models.CharField(max_length = 100, null = True)
    header_from             = models.CharField(max_length = 100, null = True)


class PolicyOverrideReason(models.Model):
    record                  = models.ForeignKey('Record')
    reason_type             = models.IntegerField(choices = choices.POLICY_REASON_TYPE, null = True)
    reason_comment          = models.CharField(max_length = 200, null = True)

class AuthResultDKIM(models.Model):
    record                  = models.ForeignKey('Record')
    domain                  = models.CharField(max_length = 100)
    selector                = models.CharField(max_length = 100, null = True)
    result                  = models.IntegerField(choices = choices.DKIM_RESULT)
    human_result            = models.CharField(max_length = 200, null = True)

class AuthResultSPF(models.Model):
    record                  = models.ForeignKey('Record')
    domain                  = models.CharField(max_length = 100)
    scope                   = models.IntegerField(choices = choices.SPF_SCOPE, null = True)
    result                  = models.IntegerField(choices = choices.SPF_RESULT)