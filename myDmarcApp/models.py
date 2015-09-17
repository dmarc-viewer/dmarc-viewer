from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.gis.db import models
from django.db.models import Sum
from polymorphic import PolymorphicModel
import choices

############################
"""
DMARC AGGREGATE REPORT MODEL
"""
############################

class Reporter(models.Model):
    org_name                = models.CharField(max_length = 100)
    email                   = models.EmailField()
    extra_contact_info      = models.CharField(max_length = 200, null = True)

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
    country_iso_code        = models.CharField(max_length = 2)
    geometry                = models.PointField(srid=4326, null = True)
    objects                 = models.GeoManager()

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
    result                  = models.IntegerField(choices = choices.DKIM_RESULT)
    human_result            = models.CharField(max_length = 200, null = True)

class AuthResultSPF(models.Model):
    record                  = models.ForeignKey('Record')
    domain                  = models.CharField(max_length = 100)
    scope                   = models.IntegerField(choices = choices.SPF_SCOPE, null = True)
    result                  = models.IntegerField(choices = choices.SPF_RESULT)

############################
"""
MYDMARC VIEW/FILTER MODEL
"""
############################

class View(models.Model):
    title                   = models.CharField(max_length = 100)
    description             = models.TextField(null = True)
    enabled                 = models.BooleanField(default = True)
    report_type             = models.IntegerField(choices = choices.REPORT_TYPE)

    def getTableData(self):
        # XXX LP: I don't like this distinct here. 
        # Do some data selection testing!!!! 
        # Django's obrm joining magic is not so predictable 
        return [{'filter_set' : filter_set, 
                 'reports': filter_set.getReports().distinct()} for filter_set in self.filterset_set.all()]

    def getLineData(self):
        """Creates data for line chart as needed by Chart.js
        y-axis: message count 
        x-axis: time
        Each day of the view time range is one x datapoint.
        It would be better to aggregate this.
        """

        # There must be exactly one 
        time_range = self.viewfilterfield_set.first()

        begin, end = time_range.getBeginEnd()
        delta = end - begin
        labels_raw = []
        labels = []
        for i in range(delta.days + 1):
            labels.append((begin + timedelta(days=i)).strftime("%B %d, %Y"))
            labels_raw.append((begin + timedelta(days=i)).date())

        data_points_count = len(labels)
        datasets = []
        for filter_set in self.filterset_set.all():
            message_count_per_day_list = filter_set.getMessageCountPerDay()

            # Create ordered data array for each label entry, add 0 if no entry in queryset
            data = []
            j = 0
            message_count_days = len(message_count_per_day_list)
            for i in range(len(labels_raw)):
                if (message_count_days > j) and \
                 (labels_raw[i] == message_count_per_day_list[j]['date']):
                    data.append(message_count_per_day_list[j]['message_count'])
                    j += 1
                else:
                    data.append(0)

            # Let's try to aggregate the data to a reasonable amount of datapoints on the x axis
            # LP XXX: maybe don't hardcode max_bins, but make it configurable
            # max_bins = 15
            # if data_points_count > max_bins:
            #     data_aggregated = []

            #     bin_size = data_points_count / max_bins
            #     bin_size_last = data_points_count % max_bins

            #     for i in range(0, data_points_count - 1, bin_size):
            #         #Aggregate
            #         if bin_size_last and i >= bin_size * max_bins:
            #             bin = bin_size_last
            #         else:
            #             bin = bin_size

            #         value_aggregated = 0
            #         for j in range(i + bin - 1):
            #            value_aggregated += data[j]

            #         data_aggregated.append(value_aggregated)

            #     data = data_aggregated



            datasets.append({'label' : str(filter_set.label), 
                             'strokeColor': str(filter_set.color), 
                             'pointHighlightStroke': str(filter_set.color),
                             'data': data})

        return {'labels': labels, 'datasets': datasets}

class FilterSet(models.Model):
    view                    = models.ForeignKey('View')
    label                   = models.CharField(max_length = 100)
    color                   = models.CharField(max_length = 7)
    multiple_dkim           = models.NullBooleanField()

    def getReports(self):
        filter_fields = [filterfield for filterfield in self.filtersetfilterfield_set.all()] + \
            [filterfield for filterfield in self.view.viewfilterfield_set.all()]

        filters = [filter_field.getFilter() for filter_field in filter_fields]
        filter_str = ".".join(filters)

        # XXX LP: Eval is dangerous especially if there is user input involved
        # Put some thought on this!!!!!!!!!!!!!!!
        return eval("Report.objects." + filter_str)


    def getMessageCountPerDay(self):
        return self.getReports()\
                .extra(select={'date': "date_range_begin::date"})\
                .values('date')\
                .annotate(message_count=Sum('record__count'))\
                .values('date', 'message_count')\
                .order_by('date')

class FilterField(PolymorphicModel):
    class Meta:
        abstract = True

class FilterSetFilterField(FilterField):
    foreign_key             = models.ForeignKey('FilterSet')
    def getFilter(self):
        key = self.report_field.replace('.', "__").lower()
        return "filter(%s=%r)" % (key, self.value)

class ViewFilterField(FilterField):
    foreign_key             = models.ForeignKey('View')

class TimeFixed(ViewFilterField):
    # max one per view
    # either time fixed or time variable
    date_range_begin        = models.DateTimeField()
    date_range_end          = models.DateTimeField()

    def getBeginEnd(self):
        return self.date_range_begin, self.date_range_end

    def getFilter(self):
        return "filter(date_range_begin__gte='%s', date_range_begin__lte='%s')" \
                % (self.getBeginEnd())

    def __str__(self):
        return "%s - %s" % (self.getBeginEnd())

class TimeVariable(ViewFilterField):
    # Creates period for last <quantity> <unit>
    # needs method that clacs date_range_begin and date_range_end
    # max one per view
    # either time fixed or time variable
    unit                    = models.IntegerField(choices = choices.TIME_UNIT)
    quantity                = models.IntegerField()

    def getBeginEnd(self):
        end = datetime.now()
        if (self.unit == choices.TIME_UNIT_DAY):
            begin = end - relativedelta(days=self.quantity)
        elif (self.unit == choices.TIME_UNIT_WEEK):
            begin = end - relativedelta(weeks=self.quantity)
        elif (self.unit == choices.TIME_UNIT_MONTH):
            begin = end - relativedelta(months=self.quantity)
        elif (self.unit == choices.TIME_UNIT_YEAR):
            begin = end - relativedelta(years=self.quantity)
        else:
            raise #Raise proper Exception
        return begin, end

    def getFilter(self):
        return "filter(date_range_begin__gte='%s', date_range_begin__lte='%s')" \
                % (self.getBeginEnd())
    def __str__(self):
        return "%s - %s" % (self.getBeginEnd())

class ReportSender(FilterSetFilterField):
    report_field            = "Reporter.email"
    value                   = models.CharField(max_length = 100)

class ReportReceiverDomain(FilterSetFilterField):
    report_field            = "domain"
    value                   = models.CharField(max_length = 100)

class SourceIP(FilterSetFilterField):
    """let's start with simple IP address filtering 
    and maybe consider CIDR notation later"""
    report_field            = "Record.source_ip"
    value                   = models.GenericIPAddressField()

class RawDkimDomain(FilterSetFilterField):
    report_field            = "Record.AuthResultDKIM.domain"
    value                   = models.CharField(max_length = 100)

class RawDkimResult(FilterSetFilterField):
    report_field            = "Record.AuthResultDKIM.result"
    value                   = models.IntegerField(choices = choices.DKIM_RESULT)

class RawSpfDomain(FilterSetFilterField):
    report_field            = "Record.AuthResultSPF.domain"
    value                   = models.CharField(max_length = 100)

class RawSpfResult(FilterSetFilterField):
    report_field            = "Record.AuthResultSPF.result"
    value                   = models.IntegerField(choices = choices.SPF_RESULT)

class AlignedDkimResult(FilterSetFilterField):
    report_field            = "Record.dkim"
    value                   = models.IntegerField(choices = choices.DMARC_RESULT)

class AlignedSpfResult(FilterSetFilterField):
    report_field            = "Record.spf"
    value                   = models.IntegerField(choices = choices.DMARC_RESULT)

class Disposition(FilterSetFilterField):
    report_field            = "Record.disposition"
    value                   = models.IntegerField(choices = choices.DISPOSITION_TYPE)
