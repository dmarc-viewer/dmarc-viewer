"""
<Program Name>
    models.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    Jun 10, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Django/DB model for DMARC aggregate reports and dmarc_viewer
    entities, e.g. views, filtersets, ...

"""


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q, F

from django.db import models
from django.contrib.contenttypes.fields import (GenericForeignKey,
        GenericRelation)
from django.db.models.fields.related import ForeignKey
from django.db.models import Sum, Count, Max
import choices



class Reporter(models.Model):
    org_name = models.CharField(max_length=100)
    email = models.EmailField()
    extra_contact_info = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.org_name

class Report(models.Model):
    """In the Schema a report is called feedback"""
    # Custom field to easily differ between incoming and outgoing
    report_type = models.IntegerField(choices=choices.REPORT_TYPE)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True)

    # MD5 hash to detect duplicate reports when parsing
    report_hash = models.CharField(max_length = 32)

    # Meta Data
    report_id = models.CharField(max_length=200)
    date_range_begin = models.DateTimeField()
    date_range_end = models.DateTimeField()

    version = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    reporter = models.ForeignKey("Reporter")

    # Policy Published
    domain = models.CharField(max_length=100)
    adkim = models.IntegerField(choices=choices.ALIGNMENT_MODE, null=True)
    aspf = models.IntegerField(choices=choices.ALIGNMENT_MODE, null=True)
    p = models.IntegerField(choices=choices.DISPOSITION_TYPE)
    sp = models.IntegerField(choices=choices.DISPOSITION_TYPE, null=True)
    pct = models.IntegerField(null=True)
    fo = models.CharField(max_length=8, null=True)

    @staticmethod
    def getOldestReportDate(report_type=choices.INCOMING):
        date_qs = Report.objects.order_by("date_range_begin")\
                .filter(report_type=report_type)\
                .values("date_range_begin").first()
        if date_qs:
            return date_qs["date_range_begin"]
        else:
            return None

    @staticmethod
    def getOverviewSummary(report_type=choices.INCOMING):
        return {
            "domain_cnt" : Report.objects.filter(
                    report_type=report_type).distinct("domain").count(),
            "report_cnt" : Report.objects.filter(
                    report_type=report_type).count(),
            "message_cnt" : Record.objects.filter(
                    report__report_type=report_type).aggregate(
                    cnt=Sum("count"))["cnt"],
            # Query per result aggregated message count for dkim, spf and dispostion
            # Transform result number to display name
            "dkim" : [
                {
                    "cnt": res["cnt"],
                    "label": dict(choices.DMARC_RESULT).get(res["dkim"])
                }
                for res in Record.objects.filter(
                        report__report_type=report_type).values(
                        "dkim").annotate(cnt=Sum("count"))
            ],

            "spf" : [
                {
                    "cnt": res["cnt"],
                    "label": dict(choices.DMARC_RESULT).get(res["spf"])
                } for res in Record.objects.filter(
                        report__report_type=report_type).values(
                        "spf").annotate(cnt=Sum("count"))
            ],
            "disposition" : [
                {
                    "cnt": res["cnt"],
                    "label": dict(choices.DISPOSITION_TYPE).get(
                            res["disposition"])
                } for res in Record.objects.filter(
                        report__report_type=report_type).values(
                        "disposition").annotate(cnt=Sum("count"))
            ],
        }

class ReportError(models.Model):
    report = models.ForeignKey("Report")
    error = models.CharField(max_length=200)

class Record(models.Model):
    report = models.ForeignKey("Report")

    # Row
    source_ip = models.GenericIPAddressField(null=True)
    country_iso_code = models.CharField(max_length=2, null=True)

    count = models.IntegerField()

    # Policy Evaluated
    disposition = models.IntegerField(choices=choices.DISPOSITION_TYPE)
    dkim = models.IntegerField(choices=choices.DMARC_RESULT)
    spf = models.IntegerField(choices=choices.DMARC_RESULT)

    # Identifiers
    envelope_to = models.CharField(max_length=100, null=True)
    envelope_from = models.CharField(max_length=100, null=True)
    header_from = models.CharField(max_length=100, null=True)

    # Custom field for filter convenience (needs one join less)
    auth_result_dkim_count = models.IntegerField(default=0)

class PolicyOverrideReason(models.Model):
    record = models.ForeignKey("Record")
    reason_type = models.IntegerField(choices=choices.POLICY_REASON_TYPE,
            null = True)
    reason_comment = models.CharField(max_length=200, null=True)

class AuthResultDKIM(models.Model):
    record = models.ForeignKey("Record")
    domain = models.CharField(max_length=100)
    result = models.IntegerField(choices=choices.DKIM_RESULT)
    human_result = models.CharField(max_length=200, null=True)

class AuthResultSPF(models.Model):
    record = models.ForeignKey("Record")
    domain = models.CharField(max_length=100)
    scope = models.IntegerField(choices=choices.SPF_SCOPE, null=True)
    result = models.IntegerField(choices=choices.SPF_RESULT)

############################
"""
DMARC viewer VIEW/FILTER MODEL

Notes:
- FilterFields that reference same Model Field are ORed
- FilterFields that reference different Model Fields are ANDed
"""
############################
#
class OrderedModel(models.Model):
    position = models.PositiveIntegerField(default=0)

    def save(self):
        """If new assign order number (max(order of all objects) or 0)
        If exists save normal."""

        if not self.id:
            try:
                self.position = self.__class__.objects.aggregate(
                        Max("position")).get("position__max", 0) + 1
            except Exception, e:
                # Default anyways, do this for more explicitness
                self.position = 0

        super(OrderedModel, self).save()

    @staticmethod
    def order(orderedObjects):
        """Assign index as order and save to each object of ordered object list"""
        for idx, obj in enumerate(orderedObjects):
            obj.position = idx
            obj.save()

    class Meta:
        ordering = ["position"]
        abstract = True


class View(OrderedModel):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True)
    enabled = models.BooleanField(default=True)
    type_map = models.BooleanField(default=True)
    type_table = models.BooleanField(default=True)
    type_line = models.BooleanField(default=True)


    def getViewFilterFieldManagers(self):
        return _get_related_managers(self, ViewFilterField)

    def getTableRecords(self):
        # Combine filters (getQuery) of all Filtersets
        query = reduce(lambda x, y: x | y,
                [fs.getQuery() for fs in self.filterset_set.all()])

        return Record.objects.filter(query).distinct().order_by(
                "report__date_range_begin") #.values_list("id", flat=True)
        # use this for list comprehension
        # PROBLEM: can't assign filterset label or color if it is all combined

    @staticmethod
    def getTableOrderFields():
        return ["report__reporter__org_name",
                "report__domain",
                "dkim",
                "spf",
                "disposition",
                "", # raw dkim domains/results are not ordered
                "", # raw dkim domains/results are not ordered
                "count",
                "source_ip",
                "country_iso_code",
                "report__date_range_begin",
                "report__date_range_end",
                "report__report_id"]

    @staticmethod
    def getTableHead():
        return ["Reporter", "Reportee", "aln. DKIM", "aln. SPF", "Disposition",
                "DKIM result", "SPF result", "msg#", "IP", "Country",
                "Report Begin", "Report End", "Report ID"]

    def getTableData(self, records=None):

        #If records is specified, use it instead of
        #this view's entire records. This can be useful for pagination"""
        if records is None:
            records = self.getTableRecords()

        return [
            [
                r.report.reporter.org_name,
                r.report.domain,
                r.get_dkim_display(),
                r.get_spf_display(),
                r.get_disposition_display(),
                "<br>".join([
                    "{0} ({1})".format(dkim.domain, dkim.get_result_display())
                        for dkim in r.authresultdkim_set.all()
                ]),
                "<br>".join([
                    "{0} ({1})".format(spf.domain, spf.get_result_display())
                        for spf in r.authresultspf_set.all()
                ]),
                r.count,
                r.source_ip,
                r.country_iso_code,
                r.report.date_range_begin.strftime("%Y/%m/%d"),
                r.report.date_range_end.strftime("%Y/%m/%d"),
                # distinct records vs. filter set labled records
                # fs.label] for fs in self.filterset_set.all() for r in self.getTableRecords()]
                r.report.report_id
            ]
            for r in list(records)
        ]

    def getCsvData(self):
        return [View.getTableHead()] + self.getTableData()

    def getLineData(self):
        # There must only one of both exactly one
        date_range = DateRange.objects.filter(foreign_key=self.id).first()
        if not date_range:
            # XXX LP Raise proper exception
            raise Exception("You have to specify a date range, you bastard!")
        begin, end = date_range.getBeginEnd()

        return {
            "begin" : begin.strftime("%Y%m%d"),
            "end" : end.strftime("%Y%m%d"),
            "data_sets" : [
                {
                    "label" : filter_set.label,
                    "color" : filter_set.color,
                    "data" : list(filter_set.getMessageCountPerDay())
                } for filter_set in self.filterset_set.all()
            ]
        }

    def getMapData(self):
        return [
            {
                "label": filter_set.label,
                "color": filter_set.color,
                "data" : list(filter_set.getMessageCountPerCountry())
            } for filter_set in self.filterset_set.all()
        ]

class FilterSet(models.Model):
    view = models.ForeignKey("View")
    label = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    multiple_dkim = models.NullBooleanField()

    def getQuery(self):
        # Get a list of object managers, each of which contains according
        # filter field objects of one class
        filter_field_managers = [
            manager for manager in self.getFilterSetFilterFieldManagers()
            ] + [
            manager for manager in self.view.getViewFilterFieldManagers()
            ]

        #All filter fields of same class are ORed
        or_queries = []
        for manager in filter_field_managers:
            filter_fields = manager.all()
            if filter_fields:
                or_queries.append(
                        reduce(lambda x, y: x | y, [
                                filter_field.getRecordFilter()
                                for filter_field in filter_fields
                                ]
                            )
                        )

        # All filter fields of different classes are ANDed
        if or_queries:
            return reduce(lambda x, y: x & y, [
                    or_query for or_query in or_queries
                    ]
                )
        else:
            return Q()

    def getMessageCountPerDay(self):
        # XXX LP: to_char is postgres specific, do we care for db flexibility?

        # Needs filter(id__in=distinct_records) workaround because
        # filter(self.getQuery()) does some db joining which can result in
        # duplicate record rows that we can't "distinct()" away when using
        # annotate()

        # Note: tried to use  Record.objects.filter(self.getQuery()).query
        # as subquery with .raw()-sql query
        # didn't work because of django quotation bug
        # https://code.djangoproject.com/ticket/17741

        # Query returns distinct `Record` ids matching the View's and View's
        # Filterset's criteria (domains, date range, ...)
        distinct_records = Record.objects.filter(
                self.getQuery()).distinct().values("id")


        # Query retrieves the sum of Records per date for above filtered
        # Reports, ordered by date in ascending order
        return Record.objects.filter(id__in=distinct_records).values(
                "report__date_range_begin").extra(
                select={
                    "date" : ("to_char(website_report.date_range_begin, 'YYYYMMDD')")
                    }
                ).values("date").annotate(cnt=Sum("count")).values(
                "date", "cnt").order_by("date")

    def getMessageCountPerCountry(self):
        distinct_records = Record.objects.filter(
                self.getQuery()).distinct().values("id")

        return Record.objects.filter(
                id__in=distinct_records).values(
                "country_iso_code").annotate(cnt=Sum("count")).values(
                "country_iso_code", "cnt")

    def getFilterSetFilterFieldManagers(self):
        return _get_related_managers(self, FilterSetFilterField)


class FilterSetFilterField(models.Model):
    foreign_key = models.ForeignKey("FilterSet")

    def getRecordFilter(self):
        key = self.record_field.replace(".", "__").lower()
        return Q(**{key: self.value})

    class Meta:
        abstract = True

class ViewFilterField(models.Model):
    foreign_key = models.ForeignKey("View")
    class Meta:
        abstract = True

class ReportType(ViewFilterField):
    value = models.IntegerField(choices=choices.REPORT_TYPE)
    def getRecordFilter(self):
        return Q(**{"report__report_type": self.value})

class DateRange(ViewFilterField):
    """
    Either DATE_RANGE_TYPE_FIXED or DATE_RANGE_TYPE_VARIABLE
    """
    dr_type = models.IntegerField(choices=choices.DATE_RANGE_TYPE)
    begin = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    unit = models.IntegerField(choices=choices.TIME_UNIT, null=True)
    quantity = models.IntegerField(null=True)

    def getBeginEnd(self):
        if (self.dr_type == choices.DATE_RANGE_TYPE_FIXED):
            return self.begin, self.end
        elif (self.dr_type == choices.DATE_RANGE_TYPE_VARIABLE):
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
                raise # XXX LP proper Exception
            return begin, end
        else:
            raise # XXX LP proper Exception

    def getRecordFilter(self):
        begin, end = self.getBeginEnd()
        return Q(**{
                    "report__date_range_begin__gte" : begin
                }) & Q(**{
                    "report__date_range_begin__lte": end
                })

    def __str__(self):
        return "{0} - {1}".format(*self.getBeginEnd())


class ReportSender(FilterSetFilterField):
    record_field = "Report.Reporter.org_name"
    value = models.CharField(max_length=100)

class ReportReceiverDomain(FilterSetFilterField):
    record_field = "Report.domain"
    value = models.CharField(max_length=100)

class SourceIP(FilterSetFilterField):
    """Filters on mail sender IP. Knows v4 and v6.
    XXX CIDR would be cool """
    record_field = "source_ip"
    value = models.GenericIPAddressField()

class RawDkimDomain(FilterSetFilterField):
    record_field = "AuthResultDKIM.domain"
    value = models.CharField(max_length=100)

class RawDkimResult(FilterSetFilterField):
    record_field = "AuthResultDKIM.result"
    value = models.IntegerField(choices=choices.DKIM_RESULT)

class MultipleDkim(FilterSetFilterField):
    value = models.BooleanField(default=False)
    def getRecordFilter(self):
        return Q(**{"auth_result_dkim_count__gt" : 1})

class RawSpfDomain(FilterSetFilterField):
    record_field = "AuthResultSPF.domain"
    value = models.CharField(max_length=100)

class RawSpfResult(FilterSetFilterField):
    record_field = "AuthResultSPF.result"
    value = models.IntegerField(choices=choices.SPF_RESULT)

class AlignedDkimResult(FilterSetFilterField):
    record_field = "dkim"
    value = models.IntegerField(choices=choices.DMARC_RESULT)

class AlignedSpfResult(FilterSetFilterField):
    record_field = "spf"
    value = models.IntegerField(choices=choices.DMARC_RESULT)

class Disposition(FilterSetFilterField):
    record_field = "disposition"
    value = models.IntegerField(choices=choices.DISPOSITION_TYPE)


def _get_related_managers(obj, parent_class=False):
    # XXX LP _get_fields is a rather internal django function,
    # not sure if I should use it here
    foreign_object_relations = obj._meta._get_fields(False)
    foreign_managers = []

    for rel in foreign_object_relations:
        # Check for parent class if wanted
        if parent_class and not issubclass(rel.related_model, parent_class):
            continue
        foreign_managers.append(getattr(obj, rel.get_accessor_name()))
    return foreign_managers

def _get_related_objects(obj, parent_class=False):
    """Helper method to get an object's foreign key related objects.
        Satisfying polymorphism workaround. Get related objects of a FilterSet.
        Alternatives might be:
            The contenttypes framework (too complicated)
            django_polymorphic (based on above, tried but did not work as expected)

    Params:
        parent_class (default false)
            related object's class must be (a subclass) of type parent_class
    Returns:
        list of related objects

    XXX LP maybe use chain from itertools for better performance

    """
    foreign_managers = _get_related_managers(obj, parent_class)
    # Get objects
    related_objects = []
    for manager in foreign_managers:
       related_objects += manager.all()

    return related_objects

def _clone(obj, parent_obj = False):
    """recursivly clone an object and its related objects"""

    related_objects = _get_related_objects(obj)
    obj.pk = None

    # If we got a parent_object, obj is already related
    # lets assign parent_object's id as foreign key
    if parent_obj:
        for field in obj._meta.fields:
            if (isinstance(field, ForeignKey) and
                    isinstance(parent_obj, field.related_model)):
                setattr(obj, field.name, parent_obj)
    # saving without pk, will auomatically create new record
    obj.save()

    for related_object in related_objects:
        _clone(related_object, obj)