"""
<Program Name>
    views.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    June, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Provide Model View Controller (MVC) view functions for this website.

    See https://docs.djangoproject.com/en/1.11/topics/http/views/ for more
    information about Django MVC views.

    NOTE:
    MVC views are not to be mistaken for analysis views. The latter constitute
    a particular view on the DMARC aggregate report data, to be displayed on
    the Deep Analysis page of this website.

"""
import json
import time
import datetime
import csv
import cairosvg

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import (HttpResponse,
        HttpResponseRedirect, StreamingHttpResponse)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import ensure_csrf_cookie

from website.forms import ViewForm, FilterSetFormSet
from website.models import (View, DateRange, Report, Reporter, AuthResultDKIM,
        AuthResultSPF, OrderedModel, _clone)
from website import choices
from website.decorators import disabled_in_demo


def overview(request):
    """Render `Overview` page with general statistics about all the DMARC
    aggregate report data between the oldest and newest outgoing and incoming
    reports. The actual statistics are fetched asynchronously so that the bare
    page is loaded faster. """
    response = {
            "start_incoming": Report.getOldestReportDate(choices.INCOMING),
            "start_outgoing": Report.getOldestReportDate(choices.OUTGOING),
            "choices": choices
    }

    return render(request, "website/overview.html", response)


@cache_page(60 * 60 * 24)
def overview_async(request):
    """Return JSON formatted statistics about DMARC aggregate report data per
    report type, i.e. incoming or outgoing, for `Overview` page. Aggregate
    reports are usually sent and received on a daily basis, so it should be
    save to cache the statistics for a day, using the `@cache_page` decorator.
    """
    report_type = int(request.GET.get("report_type"))
    response = Report.getOverviewSummary(report_type)

    return HttpResponse(json.dumps(response), content_type="application/json")


@disabled_in_demo("Cloning analysis views is disabled in this demo.")
def clone(request, view_id=None):
    """Clone the passed (by id) analysis view and redirect to `View Management`
    page. """
    try:
        view = View.objects.get(pk=view_id)
        _clone(view)

        messages.add_message(request, messages.SUCCESS,
                "Successfully cloned view '%s'" % (view.title,))

    #FIXME: See dmarc-viewer/dmarc-viewer#2
    except Exception as e:
        messages.add_message(request, messages.ERROR,
                "Something went wrong while cloning")
        raise e

    return redirect(view_management)


@disabled_in_demo("Adding or editing analysis views is disabled in this demo.")
def edit(request, view_id=None):
    """On `GET` open analysis view editor for new or existing view. On `POST`
    save new or edited view and, in case of success, redirect to `View
    Management` or `Deep Analysis` page, or, in case of invalid form data, open
    view editor and show helpful messages on how to fix the form.
    """
    if request.method == "POST":
        data = request.POST

    else:
        data = None

    # An existing `view_id` means that a particular view should be edited
    # or was edited.
    if view_id:
        try:
            view = View.objects.get(pk=view_id)

        #FIXME: See dmarc-viewer/dmarc-viewer#2
        except Exception as e:
            raise e

    else:
        view = None

    # Create forms and related form sets using optionally passed form data
    # and corresponding view
    view_form = ViewForm(data=data, instance=view)
    filter_set_formset = FilterSetFormSet(data=data, instance=view)

    # Calculate the number of (remaining) filter sets after this request. We
    # use this value for additional (non-)form validation, i.e. we require at
    # least one filter set on the view.
    # NOTE: Alternatively, we could have `FilterSetFormSet`'s clean method do
    # this automatically by passing `min_num=1` and `validate_min=True` to
    # `inlineformset_factory`, which might be cleaner but would make it harder
    # to customize the error message (see `formset.non_form_errors()`).
    real_filter_set_count = (filter_set_formset.total_form_count()
            - len(filter_set_formset.deleted_forms))

    # Posted data is used to add as new view or modify an existing view
    if request.method == "POST":
        # Save view if forms are valid and there is at least one filter set
        if (view_form.is_valid() and filter_set_formset.is_valid() and
                real_filter_set_count):
            view = view_form.save()
            filter_set_formset.instance = view
            filter_set_formset.save()
            messages.add_message(request, messages.SUCCESS,
                    "Successfully saved view '%s'." % (view.title,))

            # User clicked the "Save and show View" so we redirect to the `Deep
            # Analysis` page
            if request.POST.get("redirect_to_analysis"):
                return redirect("deep_analysis", view_id=view.id)

            return redirect("view_management")

        elif not real_filter_set_count:
            messages.add_message(request, messages.ERROR,
                    "You have to add at least one filter set to create a view."
                    " Or create multiple filter sets to compare different"
                    " aspects of your report data.")

        else:
            messages.add_message(request, messages.ERROR,
                    "Could not save analysis view. Please review your inputs.")

    return render(request, "website/view-editor.html", {
            "view_form": view_form,
            "filter_set_formset": filter_set_formset
        })


def choices_async(request):
    """Return JSON data for HTML multiselect elements that load their options
    dynamically (on type) using the passed (as GET parameter) query string.
    """
    report_type = request.GET.get("report_type")
    choice_type = request.GET.get("choice_type")
    query_str = request.GET.get("query_str")

    if choice_type == "reporter":
        values = Reporter.objects.filter(
                    report__report_type=report_type
                ).filter(
                    email__icontains=query_str
                ).distinct().order_by(
                    "org_name"
                ).values_list("org_name")

    elif choice_type == "reportee":
        values = Report.objects.filter(
                    report_type=report_type
                ).filter(
                    domain__contains=query_str
                ).distinct().order_by(
                    "domain"
                ).values_list("domain", flat=True)

    elif choice_type == "dkim_domain":
        values = AuthResultDKIM.objects.filter(
                    record__report__report_type=report_type
                ).filter(
                    domain__contains=query_str
                ).distinct().order_by(
                    "domain"
                ).values_list("domain")

    elif choice_type == "spf_domain":
        values = AuthResultSPF.objects.filter(
                    record__report__report_type=report_type
                ).filter(
                    domain__contains=query_str
                ).distinct().order_by(
                    "domain"
                ).values_list("domain")

    else:
        values = []

    return HttpResponse(json.dumps({"choices": list(values)}),
            content_type="application/json")


@disabled_in_demo("Deleting analysis views is disabled in this demo.")
def delete(request, view_id):
    """Delete analysis view by passed view id and redirect to `View Management`
    page. """
    #FIXME: See dmarc-viewer/dmarc-viewer#2
    view = View.objects.get(pk=view_id)
    view.delete()

    messages.add_message(request, messages.SUCCESS,
            "Successfully deleted view '%s'." % (view.title,))

    return redirect("view_management")


@disabled_in_demo("Re-ordering analysis views is disabled in this demo.")
def order(request):
    """Receive a JSON formatted ordered list of view ids and re-order view
    objects accordingly using `OrderedModel`'s static order method. """
    try:
        view_ids = json.loads(request.body)
        views = []

        for view_id in view_ids:
            views.append(View.objects.get(pk=view_id))

        OrderedModel.order(views)

        messages.add_message(request, messages.SUCCESS,
                "Successfully sorted views.")

    #FIXME: See dmarc-viewer/dmarc-viewer#2
    except Exception as e:
        messages.add_message(request, messages.ERROR, "Sorting did not work.")
        raise e

    return HttpResponse(json.dumps({}), content_type="application/json")


def export_svg(request, view_id):
    """Export analysis view map or line chart as pdf for a passed view (by id).
    """
    #FIXME: See dmarc-viewer/dmarc-viewer#2

    # Extract SVG data and type (map or line chart) from POST request
    svg_data = request.POST.get("svg")
    view_type = request.POST.get("view_type")

    # Variables used for the title of the exported file
    view = View.objects.get(pk=view_id)
    date = datetime.datetime.now().strftime("%Y%m%d")

    # Create pdf
    # NOTE: Cairo replaced svglib.svglib.SvgRenderer, xml.dom.minidom and
    # reportlab.graphics.renderPDF (also works with stylesheets and clippath)
    pdf = cairosvg.svg2pdf(svg_data)

    response = HttpResponse(content_type="application/pdf")

    # Modify response header, so that the browser "downloads" to returned data
    response["Content-Disposition"] = "attachment; filename='%s_%s_%s.pdf'" % (
            view.title, view_type, date)

    # `HttpResponse` is a file-like object to which we can write the PDF data
    response.write(pdf)

    return response


class Echo(object):
    """An class that implements a write method for a file-like interface
    used for CSV streaming. """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def export_csv(request, view_id):
    """Export analysis view table as comma separated values (CSV) file for a
    passed view (by id).
    """
    view = View.objects.get(pk=view_id)
    date = datetime.datetime.now().strftime("%Y%m%d")

    csv_data = view.getCsvData()
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    # We have to stream the response since the file might be huge
    response = StreamingHttpResponse(
            (writer.writerow(row) for row in csv_data),
            content_type="text/csv")

    response["Content-Disposition"] = "attachment; filename='%s_%s.csv'" % (
            view.title, date)

    return response


@ensure_csrf_cookie
def view_management(request):
    """Render `View Management` page, showing all available analysis views.
    The page needs a csrf token used for async view ordering. That's why we
    enforce it using the `@ensure_csrf_cookie` decorator.
    """
    return render(request, "website/view-management.html",
            {"views": View.objects.all()})


def deep_analysis_first(request):
    """Helper view to render the first analysis view in the db on the `Deep
    Analysis` page, or redirect to the `View Management` page, if no view
    exists.
    """
    view = View.objects.first()

    if not view:
        messages.add_message(request, messages.WARNING,
                "You should start adding views before you want to use them.")

        return redirect("view_management")

    return redirect("deep_analysis", view_id=view.id)


@ensure_csrf_cookie
def deep_analysis(request, view_id):
    """Render `Deep Analysis` page to show DMARC aggregate report data for the
    passed view (by id) and a sidebar with links to all (enabled) views.
    The actual report data is loaded asynchronously to reduce waiting time.
    The page also needs a csrf token used for async pdf/csv exports. That's
    why we enforce it using the `@ensure_csrf_cookie` decorator.
    """
    try:
        view = View.objects.get(pk=view_id)

    except View.DoesNotExist as e:
        messages.add_message(request, messages.WARNING,
                "The view you were looking for does not exist."
                " Why not choose one from below?")

        return redirect("view_management")

    sidebar_views = View.objects.filter(enabled=True).values("id", "title")

    return render(request, "website/deep-analysis.html", {
            "sidebar_views": sidebar_views,
            "the_view": view,
            "table_head": View.getTableHead()
        })


def map_async(request, view_id):
    """Return JSON formatted DMARC aggregate report data prepared for the
    passed view's (by id) map as displayed on the `Deep Analysis` page.
    """
    view = View.objects.get(pk=view_id)
    view_type_map_data = view.getMapData() if view.type_map else []

    return HttpResponse(json.dumps(view_type_map_data),
            content_type="application/json")


def line_async(request, view_id):
    """Return JSON formatted DMARC aggregate report data prepared for the
    passed view's (by id) line chart as displayed on the `Deep Analysis` page.
    """
    view = View.objects.get(pk=view_id)
    view_type_line_data = view.getLineData() if view.type_line else []

    return HttpResponse(json.dumps(view_type_line_data),
            content_type="application/json")


def table_async(request, view_id):
    """Return JSON formatted DMARC aggregate report data prepared for the
    passed view's (by id) report table as displayed on the `Deep Analysis`
    page. The data is requested via post, to allow table sorting, pagination
    and quick filtering.

    See https://datatables.net/ for more information about client-side sorting
    and pagination.
    """
    view = View.objects.get(pk=view_id)

    # Receive data as JSON POST (Django doesn't do urlencoded nested dicts)
    request_data = json.loads(request.POST.get("data"))

    # Extract table configuration parameters from posted data
    draw_counter = int(request_data.get("draw", 1))
    page_length = int(request_data.get("length", 10))
    row_index = int(request_data.get("start", 0))
    time_filter = request_data.get("custom_filters").get("time")

    # Get all (unfiltered) records for this view from the db
    records = view.getTableRecords()
    records_total = records.count()
    records_filtered = records_total

    # Filter table rows based on time, using an on-the-fly `DateRange` filter
    if time_filter:
        try:
            date_range_tmp = DateRange()
            date_range_tmp.dr_type = choices.DATE_RANGE_TYPE_FIXED
            date_range_tmp.begin = datetime.datetime.strptime(
                    time_filter[0], "%Y-%m-%dT%H:%M:%S.%fZ")
            date_range_tmp.end = datetime.datetime.strptime(time_filter[1],
                    "%Y-%m-%dT%H:%M:%S.%fZ")
            date_range_filter = date_range_tmp.getRecordFilter()
            records = records.filter(date_range_filter)
            records_filtered = records.count()

        #FIXME: See dmarc-viewer/dmarc-viewer#2
        except Exception as e:
            pass

    # Order
    # NOTE: Beware of multicolumn sort!!
    order = request_data.get("order")[0]
    columns = request_data.get("columns")
    order_idx = int(order["column"])

    if columns[order_idx]["orderable"]:
        order_by = View.getTableOrderFields()

        prefix = "-" if order["dir"] == "desc" else ""
        records = records.order_by(prefix + order_by[order_idx])

    # Paginate
    paginator = Paginator(records, page_length)
    # Get 1-based page index
    page_index = row_index / page_length + 1
    # Get the records for wanted page
    try:
        data = paginator.page(page_index)

    except PageNotAnInteger:
        data = paginator.page(1)

    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    # Get table data for the filtered and paginated records only
    page_data = view.getTableData(data)

    resp = {
        "draw": draw_counter,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": page_data
    }

    return HttpResponse(json.dumps(resp), content_type="application/json")


def help_page(request):
    """Render static "Help" page. """
    return render(request, "website/help.html")

