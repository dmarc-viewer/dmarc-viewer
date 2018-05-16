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
    Main DMARC viewer model definition for Django's object-relational mapping.
    See https://docs.djangoproject.com/en/1.11/topics/db/models/

    This module defines models for
        - DMARC aggregate reports, and
        - DMARC viewer analysis views


    See https://tools.ietf.org/html/rfc7489#appendix-C for DMARC aggregate
    report schema.
    To parse the XML reports use the management command defined in
    `website.management.commands.parse`.

    DMARC viewer analysis views define sets of filters to query stored DMARC
    aggregate report data by time range, report type (incoming or outgoing),
    and other report properties.

    See `demo/view.json` for initial demo views. Use the managment command
    defined in `website.management.commands.loadviews` to parse demo views.

    The models also include methods to query DMARC report data based on
    analysis view filters.

"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q

from django.db import models
from django.contrib.contenttypes.fields import (GenericForeignKey,
        GenericRelation)
from django.db.models.fields.related import ForeignKey
from django.db.models import Sum, Count, Max
from django.db.models.functions import TruncDay

import choices




"""DMARC Aggregate Report Models

See https://tools.ietf.org/html/rfc7489#appendix-C for infos about the fields.

"""
class Reporter(models.Model):
    org_name = models.CharField(max_length=100)
    email = models.EmailField()
    extra_contact_info = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.org_name



class Report(models.Model):
    """In the schema a report is called feedback"""
    # Custom field to easily differ between incoming and outgoing
    report_type = models.IntegerField(choices=choices.REPORT_TYPE)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True)

    # MD5 hash to detect duplicate reports when parsing
    report_hash = models.CharField(max_length = 32)

    # Meta data
    report_id = models.CharField(max_length=200)
    date_range_begin = models.DateTimeField()
    date_range_end = models.DateTimeField()

    version = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    reporter = models.ForeignKey("Reporter")

    # Policy published
    domain = models.CharField(max_length=100)
    adkim = models.IntegerField(choices=choices.ALIGNMENT_MODE, null=True)
    aspf = models.IntegerField(choices=choices.ALIGNMENT_MODE, null=True)
    p = models.IntegerField(choices=choices.DISPOSITION_TYPE)
    sp = models.IntegerField(choices=choices.DISPOSITION_TYPE, null=True)
    pct = models.IntegerField(null=True)
    fo = models.CharField(max_length=8, null=True)


    @staticmethod
    def getOldestReportDate(report_type=choices.INCOMING):
        """Return the date for the oldest report in the database as
        unix timestamp for a given report type, or None.
        It uses the reported begin times for report aggregation periods, which
        can be incorrect.

        This method is used to display the time range of all reports on the
        Overview page.
        """
        date_qs = Report.objects.order_by("date_range_begin"
                ).filter(report_type=report_type
                ).values("date_range_begin"
                ).first()

        if date_qs:
            return date_qs["date_range_begin"]

        else:
            return None


    @staticmethod
    def getOverviewSummary(report_type=choices.INCOMING):
        """Return statistics about aligned DKIM and SPF results and disposition
        for all stored reports of a given report type.

        This method is used to display general infos for all reports on the
        Overview page.
        """
        return {
            "domain_cnt" : Report.objects.filter(
                    report_type=report_type).distinct("domain").count(),
            "report_cnt" : Report.objects.filter(
                    report_type=report_type).count(),
            "message_cnt" : Record.objects.filter(
                    report__report_type=report_type).aggregate(
                    cnt=Sum("count"))["cnt"],

            # Query per result aggregated message count for dkim, spf and
            # disposition and transform result number to display name
            "dkim" : [
                {
                    "cnt": res["cnt"],
                    "label": dict(choices.DMARC_RESULT).get(res["dkim"])
                } for res in Record.objects.filter(
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




"""DMARC Viewer Analysis View Models

Models to define sets of filters on DMARC aggregate report data and methods
to retrieve report data from the DB applying the defined filters.

Analysis Views are the heart of this project and can be viewed in the Deep
Analysis page of the web interface. Each view can show a map, a line chart, and
a table for the filtered report data.

Views can be managed (create, edit, clone, order, delete) using the web
interface.

"""
class OrderedModel(models.Model):
    """Instances of subclasses of this abstract class receive an additional
    position field so that they can be ordered relative to other instances of
    the same subclass. """
    position = models.PositiveIntegerField(default=0)


    def save(self):
        """Override model's save method to initialize the position relative (at
        the end) to other objects of this class. """

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
        """Iterate over an ordered list of instances of a class that subclasses
        OrderedModel and re-assign each instance's position attribute. """
        for idx, obj in enumerate(orderedObjects):
            obj.position = idx
            obj.save()


    class Meta:
        ordering = ["position"]
        abstract = True



class View(OrderedModel):
    """Analysis views display the report data for the defined view filters
    (report time, report type) for each filter set pertaining to a view. Title
    and description should help the viewer to quickly understand what report
    data is displayed. """
    title = models.CharField(max_length=100)
    description = models.TextField(null=True)

    # Show/hide view on Deep Analysis page
    enabled = models.BooleanField(default=True)

    # Show/hide the different view types
    type_map = models.BooleanField(default=True)
    type_table = models.BooleanField(default=True)
    type_line = models.BooleanField(default=True)


    def getViewFilterFieldManagers(self):
        """Wrapper for internal `_get_related_managers` helper function to
        return object managers for `ViewFilterField` subclasses related to this
        view. """
        return _get_related_managers(self, ViewFilterField)


    def getTableRecords(self):
        """Return DMARC report table records for this view.

        TODO: It would be nice to annotate the query with the related filter
        set's label and color to use that info in the table. (Beware of
        duplicate rows).

        """
        # Combine non-empty filter queries from all filter sets of this view
        query = reduce(lambda x, y: x | y, [fs.getQuery()
                for fs in self.filterset_set.all()])

        return Record.objects.filter(query).distinct().order_by(
                "report__date_range_begin")


    @staticmethod
    def getTableOrderFields():
        """Return a list of DMARC report record fields in the same order as the
        corresponding table columns, used to sort datatables columns with
        django's order_by function.
        """
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
        """Return a list of DMARC report record fields display names in the
        same order as the corresponding table columns, used as column titles.
        """
        return ["Reporter", "Reportee", "aln. DKIM", "aln. SPF", "Disposition",
                "DKIM result", "SPF result", "msg#", "IP", "Country",
                "Report Begin", "Report End", "Report ID"]


    def getTableData(self, records=None):
        """Return list of DMARC report table rows for this view, replacing
        numerical values with their corresponding display value and formating
        timestamps. If no records are passed, return all records of this view.
        Passing records can be used for pagination. """
        if records is None:
            records = self.getTableRecords()

        return [
            [
                r.report.reporter.org_name,
                r.report.domain,
                r.get_dkim_display(),
                r.get_spf_display(),
                r.get_disposition_display(),
                # For simplicity we concatenate raw DKIM and SPF results
                # respectively and write each in one cell.
                # TODO: Remove HTML markup here.
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
                r.report.report_id
            ]
            for r in list(records)
        ]


    def getCsvData(self):
        """Return DMARC report table data with header as first row for this
        view. """
        return [View.getTableHead()] + self.getTableData()


    def getLineData(self):
        """Return time line chart data for this view prepared for use with
        D3.js line chart. The time line chart shows the message count per day,
        per filter set. """
        # Each view must have exactly one DateRange object
        date_range = DateRange.objects.filter(foreign_key=self.id).first()
        assert(date_range is not None)

        begin, end = date_range.getBeginEnd()
        return {
            "begin" : begin.strftime("%Y%m%d"),
            "end" : end.strftime("%Y%m%d"),
            "data_sets" : [
                {
                    "label" : filter_set.label,
                    "color" : filter_set.color,
                    "data" : [
                        {
                            "cnt": row["cnt"],
                            "date": row["date"].strftime("%Y%m%d")
                        } for row in filter_set.getMessageCountPerDay()
                    ],
                } for filter_set in self.filterset_set.all()
            ]
        }


    def getMapData(self):
        """Return map data for this view prepared for use with D3.js DataMaps.
        A separate map for every filter set is created, with message count per
        country and color gradients. """
        return [
            {
                "label": filter_set.label,
                "color": filter_set.color,
                "data" : list(filter_set.getMessageCountPerCountry())
            } for filter_set in self.filterset_set.all()
        ]



class FilterSet(models.Model):
    """Filter sets are used to compare different aspects of DMARC aggregate
    reports in the associated analysis view. Each filter set can have various
    filters. Most filter can have one or more values, hence the one-to- many
    relationship. E.g. the filter for raw DKIM results can be one or more of
    'none', 'pass', 'fail', 'policy', 'neutral', 'temperror', 'permerror'.

    NOTE: When using filters to query DMARC aggregate report data the following
    rules apply:

        - All filter fields of the same class are ORed
          E.g. Two raw DKIM result filters 'temperror' and 'permerror' returns
          all reports that have a raw DKIM result of 'temperror' **OR**
          'permerror'.

        - All filter fields of classes are ANDed
          E.g. A DKIM result filter of 'pass' and a SPF result filter of 'pass'
          returns only reports that have a DKIM **AND** SPF result of 'pass'.

    """
    view = models.ForeignKey("View")
    label = models.CharField(max_length=100)
    color = models.CharField(max_length=7)

    # A boolean filter does not need to be one-to-many
    multiple_dkim = models.NullBooleanField()


    def getQuery(self):
        """Return combined view and filter set filters for this filter set
        as complex SQL query using django's `Q` object.

        See
        https://docs.djangoproject.com/en/1.11/ref/models/querysets/#q-objects
        for more information.

        """
        # Get a list of object managers, each of which containing the
        # corresponding view and filter set filter field objects of all
        # available filter set classes.
        filter_field_managers = [
            manager for manager in self.getFilterSetFilterFieldManagers()
        ] + [
            manager for manager in self.view.getViewFilterFieldManagers()
        ]

        # Create an OR query for all filter fields of the same class
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

        # If there are different filter field OR queries, combine those
        # queries as one AND query
        if or_queries:
            return reduce(lambda x, y: x & y, [
                    or_query for or_query in or_queries
                    ]
                )
        # If the filter set does not have any filter fields, we return an empty
        # query, which is equivalent to querying all objects, e.g.:
        # `View.objects.all() == View.objects.filter(Q())`
        else:
            return Q()


    def getMessageCountPerDay(self):
        """Return list of date and message count tuples, ordered by date,
        for this filter set. """

        # NOTE: We first filter distinct record ids for this filter set
        # and then use those record ids as additional filter parameter when we
        # perform the actual query for message count by date. This workaround
        # is (?) required to not get duplicate record rows that we can't
        # `distinct` away when using `annotate`, due to some crazy db joins.
        # TODO: Revise the workaround

        # Query distinct record ids for this filter set
        distinct_records = Record.objects.filter(
                self.getQuery()).distinct().values("id")


        # Query the sum of message counts per day for above filtered
        # records, ordered by date in ascending order
        return Record.objects.filter(id__in=distinct_records).values(
                "report__date_range_begin").annotate(
                date=TruncDay("report__date_range_begin"),
                cnt=Sum("count")).values("date", "cnt").order_by("date")


    def getMessageCountPerCountry(self):
        """Return list of country and message count tuples for this filter set.
        """
        # NOTE: See note in `getMessageCountPerDay` for more info about two
        # query workaround

        # Query distinct record ids for this filter set
        distinct_records = Record.objects.filter(
                self.getQuery()).distinct().values("id")

        # Query the sum of message counts per country for above filtered
        # records, ordered by date in ascending order
        return Record.objects.filter(
                id__in=distinct_records).values(
                "country_iso_code").annotate(cnt=Sum("count")).values(
                "country_iso_code", "cnt")


    def getFilterSetFilterFieldManagers(self):
        """Wrapper for internal `_get_related_managers` helper function to
        return object managers for `FilterSetFilterField`
        subclasses related to this filter set. """
        return _get_related_managers(self, FilterSetFilterField)



class FilterSetFilterField(models.Model):
    """Abstract parent class for all filter set filter fields, which are used
    to define filters corresponding to DMARC aggregate report attributes.
    Also see `ViewFilterField` for additional info.
    """
    foreign_key = models.ForeignKey("FilterSet")


    def getRecordFilter(self):
        """Construct a django query that identifies the DMARC aggregate report
        record field, on which a given filter should be applied, using the
        filter's `record_field`. The returned query can be passed to


        Example:
        ```
        >>> sender_filter = ReportSender(value="google.com")
        >>> sender_filter.record_field
        'Report.Reporter.org_name'
        >>> query = report_sender_filter.getRecordFilter()
        >>> query
        <Q: (AND: ('report__reporter__org_name', 'google.com'))>
        >>> from website.models import Record
        >>> Record.objects.filter(query)
        <QuerySet [records with sender domain 'google.com', ...]>
        ```
        """

        # Replace dots with double underscore to get the notation that is
        # required by `Q`. Note that we could use that notation right away, but
        # IMHO dot notation, is nicer to read.
        key = self.record_field.replace(".", "__").lower()
        return Q(**{key: self.value})


    class Meta:
        abstract = True



class ViewFilterField(models.Model):
    """Abstract parent class for all view filter fields, which are used to
    define filters corresponding to DMARC aggregate report attributes.

    Note that unlike the abstract `FilterSetFilterField` above, this abstract
    class does not implement a `getRecordFilter` method because there are only
    two subclasses of `ViewFilterField` and one of them requires a custom
    `getRecordFilter` method anyway.

    It might seem more intuitive to just store the report type and date range
    filters directly on the view model, since both have a one-to-one
    relationship to a given view. However, using the same concept as for
    one-to-many filters (see `FilterSetFilterField`) makes it easier to apply
    all filters when querying report data for a view (see `getQuery`).
    """
    foreign_key = models.ForeignKey("View")


    class Meta:
        abstract = True



class ReportType(ViewFilterField):
    """View filter for report type. Value must be one of `choices.REPORT_TYPE`.
    """
    value = models.IntegerField(choices=choices.REPORT_TYPE)


    def getRecordFilter(self):
        """ See docstring of `FilterSetFilterField.getRecordFilter`. """
        return Q(**{"report__report_type": self.value})



class DateRange(ViewFilterField):
    """View filter for date range, which is either a fixed date range with
    begin and end date, or a dynamic range, i.e. "last <quantity> <unit>",
    where unit is one of `choices.TIME_UNIT`. """
    dr_type = models.IntegerField(choices=choices.DATE_RANGE_TYPE)
    begin = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    unit = models.IntegerField(choices=choices.TIME_UNIT, null=True)
    quantity = models.IntegerField(null=True)


    def getBeginEnd(self):
        """Return begin and end date for the given time range. In case of
        a fixed date range it is easy, in case of a dynamic date range, we
        have to calculate. """
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
                # This case should not happen
                raise Exception("A DateRange object's 'unit' must be a numeric"
                        " value in: {units}.".format(units=", ".join([
                        "{const} ({name})".format(const=unit, name=unit_name)
                        for unit, unit_name in choices.TIME_UNIT
                        if unit is not None]))
                )

            return begin, end

        else:
            # This case should not happen
            raise Exception("A DateRange object's 'dr_type' must be one of:"
                    " {const_fixed} (fixed range) or {const_dynamic}"
                    " (dynamic range).".format(
                    const_fixed=choices.DATE_RANGE_TYPE_FIXED,
                    const_dynamic=choices.DATE_RANGE_TYPE_VARIABLE
                    ))


    def getRecordFilter(self):
        """Special case for record filter using greater/lesser than directives.
        See docstring of `FilterSetFilterField.getRecordFilter` for generic
        case. """
        begin, end = self.getBeginEnd()
        return (Q(**{"report__date_range_begin__gte" : begin})
                & Q(**{"report__date_range_begin__lte": end}))


    def __str__(self):
        return "{0} - {1}".format(*self.getBeginEnd())


class ReportSender(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "Report.Reporter.org_name"
    value = models.CharField(max_length=100)


class ReportReceiverDomain(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "Report.domain"
    value = models.CharField(max_length=100)


class SourceIP(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "source_ip"
    # GenericIPAddressField supports v4 and v6 IP addresses.
    # TODO: Support CIDR notation.
    value = models.GenericIPAddressField()


class RawDkimDomain(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "AuthResultDKIM.domain"
    value = models.CharField(max_length=100)


class RawDkimResult(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "AuthResultDKIM.result"
    value = models.IntegerField(choices=choices.DKIM_RESULT)


class MultipleDkim(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    value = models.BooleanField(default=False)
    def getRecordFilter(self):
        return Q(**{"auth_result_dkim_count__gt" : 1})


class RawSpfDomain(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "AuthResultSPF.domain"
    value = models.CharField(max_length=100)


class RawSpfResult(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "AuthResultSPF.result"
    value = models.IntegerField(choices=choices.SPF_RESULT)


class AlignedDkimResult(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "dkim"
    value = models.IntegerField(choices=choices.DMARC_RESULT)


class AlignedSpfResult(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "spf"
    value = models.IntegerField(choices=choices.DMARC_RESULT)


class Disposition(FilterSetFilterField):
    """See docstring of `FilterSetFilterField`. """
    record_field = "disposition"
    value = models.IntegerField(choices=choices.DISPOSITION_TYPE)



def _get_related_managers(obj, parent_class=False):
    """Internal helper method to get managers for objects that are related to
    the passed object by foreign key and use class inheritance (django models
    don't work well(?) with inheritance).
    These object managers can be used to query the actual relevant objects.

    Example: Get all subclasses of `FilterSetFilterField` related to a given
    `FilterSet`.

    Optionally, returns only subclasses of a specified parent class.

    TODO: Find a better solution that does not use a non-API Django method,
    i.e. `_get_fields`.

    Tested alternatives are
    - `contenttypes` framework (overkill)
    - `django_polymorphic` (didn't work as expected)

    """
    foreign_object_relations = obj._meta._get_fields(False)
    foreign_managers = []

    for rel in foreign_object_relations:
        # Check for parent class if wanted
        if parent_class and not issubclass(rel.related_model, parent_class):
            continue
        foreign_managers.append(getattr(obj, rel.get_accessor_name()))
    return foreign_managers



def _get_related_objects(obj, parent_class=False):
    """Wrapper for `_get_related_managers` that additionally performs the db
    query on the managers to return the actual related objects. """
    foreign_managers = _get_related_managers(obj, parent_class)

    related_objects = []
    for manager in foreign_managers:
       related_objects += manager.all()

    return related_objects



def _clone(obj, fk_obj=False):
    """Recursively clone an object and its related objects.
    NOTE: If an `fk_obj` is passed and `obj` has a foreign key field to an
    object that has the same class as `fk_obj`, then `fk_obj` is assigned as
    that foreign key of `obj`. """
    related_objects = _get_related_objects(obj)

    # Set the primary key to None to create a new entry in the db
    obj.pk = None

    # If passed and relevant assign `fk_obj` as foreign key
    if fk_obj:
        for field in obj._meta.fields:
            if (isinstance(field, ForeignKey) and
                    isinstance(fk_obj, field.related_model)):
                setattr(obj, field.name, fk_obj)

    # Save so that related objects in the next recursion can use as foreign key
    obj.save()

    # Recurse
    for related_object in related_objects:
        _clone(related_object, obj)
