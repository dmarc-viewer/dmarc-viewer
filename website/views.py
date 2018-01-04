import json
import time
import datetime
import csv
import cairosvg

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import ensure_csrf_cookie

from forms import *
from website.models import View, DateRange, OrderedModel, _clone

def overview(request):
    response = {
            "start_incoming" : Report.getOldestReportDate(choices.INCOMING),
            "start_outgoing" : Report.getOldestReportDate(choices.OUTGOING),
            "choices": choices
    }

    return render(request, 'website/overview.html', response)

@cache_page(60 * 60 * 24)
def overview_async(request):
    report_type = int(request.GET.get("report_type"))
    response = Report.getOverviewSummary(report_type)
    return HttpResponse(json.dumps(response), content_type="application/json")

def clone(request, view_id = None):
    try:
        view = View.objects.get(pk=view_id)
        _clone(view)
        messages.add_message(request, messages.SUCCESS, "Successfully cloned view '%s'" % (view.title,))
    except Exception, e:
        messages.add_message(request, messages.ERROR, "Something went wrong while cloning")
        raise e
    return redirect(view_management)

def edit(request, view_id = None):
    # Assign form data if posted
    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    # if we got a view_id look if there is an according view
    if view_id:
        try:
            view = View.objects.get(pk=view_id)
        except Exception, e:
            raise e
    else:
        view = None

    # Create Forms and formsets
    view_form               = ViewForm(data=data, instance = view)
    filter_set_formset      = FilterSetFormSet(data=data, instance = view)

    if request.method == 'POST':
        valid = False
        if view_form.is_valid():
            if filter_set_formset.is_valid():
                valid = True

        if valid:
            view = view_form.save()
            filter_set_formset.instance = view
            filter_set_formset.save()
            messages.add_message(request, messages.SUCCESS, "Successfully saved view '%s'" % (view.title,))

            if request.POST.get("redirect_to_analysis"):
                return redirect("deep_analysis", view_id=view.id)
            return redirect("view_management")
        else:
            messages.add_message(request, messages.ERROR, "Could not save view.")


    return render(request, 'website/view-editor.html', {
            'view_form'               : view_form,
            'filter_set_formset'      : filter_set_formset
        })

def choices_async(request):
    report_type = request.GET.get("report_type")
    choice_type = request.GET.get("choice_type")
    query_str   = request.GET.get("query_str")

    if choice_type == "reporter":
        values = Reporter.objects.filter(
                                    report__report_type=report_type
                                ).filter(
                                    email__icontains=query_str
                                ).distinct().order_by(
                                    'org_name'
                                ).values_list('org_name')
    elif choice_type == "reportee":
        values = Report.objects.filter(
                                    report_type=report_type
                                ).filter(
                                    domain__contains=query_str
                                ).distinct().order_by(
                                    'domain'
                                ).values_list('domain', flat=True)
    elif choice_type == "dkim_domain":
        values = AuthResultDKIM.objects.filter(
                                    record__report__report_type=report_type
                                ).filter(
                                    domain__contains=query_str
                                ).distinct().order_by(
                                    'domain'
                                ).values_list('domain')
    elif choice_type == "spf_domain":
        values = AuthResultSPF.objects.filter(
                                    record__report__report_type=report_type
                                ).filter(
                                    domain__contains=query_str
                                ).distinct().order_by(
                                    'domain'
                                ).values_list('domain')
    else:
        values = []

    return HttpResponse(json.dumps({"choices": list(values)}), content_type="application/json")

def delete(request, view_id):
    # XXX: Add try catch
    # XXX: Add ask confirm in Javascript
    view = View.objects.get(pk=view_id)
    view.delete()
    messages.add_message(request, messages.SUCCESS, "Successfully deleted view '%s'" % (view.title,))
    return redirect("view_management")

def order(request):
    """Gets an orderd list of view ids. Calls OrderedModel static order method
    to save the order to view model. """

    try:
        view_ids = json.loads(request.body)
        views = []
        for view_id in view_ids:
            views.append(View.objects.get(pk=view_id))
        OrderedModel.order(views)
        messages.add_message(request, messages.SUCCESS, "Successfully sorted views.")
    except Exception, e:
        messages.add_message(request, messages.ERROR, "Sorting did not work.")
        raise e

    # XXX LP: Make nice ajax messages like in normal templates
    return HttpResponse(json.dumps({}), content_type="application/json")

def export_svg(request, view_id):

    # Get data from client side via POST variables
    svg_data = request.POST.get("svg")
    view_type = request.POST.get("view_type")

    view = View.objects.get(pk=view_id)
    date = datetime.datetime.now().strftime('%Y%m%d')

    # create pdf
    # NOTE: replaces svglib.svglib.SvgRenderer, reportlab.graphics.renderPDF, xml.dom.minidom
    # also works with stylesheets and clippath
    pdf = cairosvg.svg2pdf(svg_data)

    # Response is file-like we can write pdf to it
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "attachment; filename='%s_%s_%s.pdf'" % (view.title, view_type, date)

    response.write(pdf)

    return response

class Echo(object):
    """An object that implements just the write method of the file-like
    interface. Needed for CSV streaming
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def export_csv(request, view_id):
    view = View.objects.get(pk=view_id)
    date = datetime.datetime.now().strftime('%Y%m%d')

    csv_data = view.getCsvData()
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in csv_data),
                                     content_type="text/csv")
    response['Content-Disposition'] = "attachment; filename='%s_%s.csv'" % (view.title, date)
    return response

@ensure_csrf_cookie
def view_management(request):
    return render(request, 'website/view-management.html', {'views' : View.objects.all()})

def deep_analysis_first(request):
    view = View.objects.first()
    if not view:
        messages.add_message(request, messages.WARNING, "You should start adding views before you want to use them.")
        return redirect("view_management")
    return redirect("deep_analysis", view_id=view.id)

@ensure_csrf_cookie
def deep_analysis(request, view_id):
    try:
        view = View.objects.get(pk=view_id)
    except View.DoesNotExist as e:
        messages.add_message(request, messages.WARNING, "The view you were looking for does not exist. Why not choose one from below?")
        return redirect("view_management")

    sidebar_views = View.objects.filter(enabled='true').values('id', 'title')

    return render(request, 'website/deep-analysis.html', {
            'sidebar_views'         : sidebar_views,
            'the_view'              : view,
            'table_head'            : View.getTableHead()
        })

def map_async(request, view_id):
    view = View.objects.get(pk=view_id)
    view_type_map_data   = view.getMapData() if view.type_map else []
    return HttpResponse(json.dumps(view_type_map_data), content_type="application/json")

def line_async(request, view_id):
    view = View.objects.get(pk=view_id)

    view_type_line_data  = view.getLineData() if view.type_line else []
    return HttpResponse(json.dumps(view_type_line_data), content_type="application/json")

def table_async(request, view_id):
    view = View.objects.get(pk=view_id)

    # Get the data as posted json
    # django can't handle default urlencoded nested dicts
    request_data = json.loads(request.POST.get("data"))

    # Get configuration params
    draw_counter    = int(request_data.get("draw", 1))
    page_length     = int(request_data.get("length", 10))
    row_index       = int(request_data.get("start", 0))
    time_filter     = request_data.get("custom_filters").get("time")

    # Get all (unfiltered) records for this view
    records          = view.getTableRecords()
    records_total    = records.count()
    records_filtered = records_total

    # Filter records
    if time_filter:
        try:
            date_range_tmp = DateRange()
            date_range_tmp.dr_type  = choices.DATE_RANGE_TYPE_FIXED
            date_range_tmp.begin    = datetime.datetime.strptime(time_filter[0], '%Y-%m-%dT%H:%M:%S.%fZ')
            date_range_tmp.end      = datetime.datetime.strptime(time_filter[1], '%Y-%m-%dT%H:%M:%S.%fZ')
            date_range_filter       = date_range_tmp.getRecordFilter()
            records                 = records.filter(date_range_filter)
            records_filtered        = records.count()

        except Exception, e:
            pass


    # Ordering
    order = request_data.get("order")[0] # XXX LP: beware of multicolum sort!!
    columns = request_data.get("columns")
    order_idx = int(order["column"])

    if columns[order_idx]["orderable"]:
        order_by = View.getTableOrderFields()

        prefix = "-" if order["dir"] == "desc" else ""
        records = records.order_by(prefix + order_by[order_idx])

    # Create paginator
    # evaluate db query (list()) here
    # records = list(records)
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

    # Get the table rows for wanted records
    page_data = view.getTableData(data)

    resp = {
        "draw"             : draw_counter,
        "recordsTotal"     : records_total,
        "recordsFiltered"  : records_filtered,
        "data"             : page_data
    }
    return HttpResponse(json.dumps(resp), content_type="application/json")


def help(request):
    return render(request, 'website/help.html')

