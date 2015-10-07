import json
import time
import csv
from svglib.svglib import SvgRenderer
from reportlab.graphics import renderPDF

import xml.dom.minidom
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.contrib import messages
from forms import *
from myDmarcApp.models import View, OrderedModel, _clone

class Echo(object):
    """An object that implements just the write method of the file-like
    interface. Needed for CSV streaming
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def index(request):
    return render(request, 'myDmarcApp/overview.html',{})

"""
VIEW VIEWS BEGIN
"""
def clone(request, view_id = None):
    try:
        view = View.objects.get(pk=view_id)
        _clone(view)
        messages.add_message(request, messages.SUCCESS, "Successfully cloned view.")
    except Exception, e:
        messages.add_message(request, messages.ERROR, "You are such a prick!")
        raise e
    return redirect(view_management)

def edit(request, view_id = None):
    """Check filterset_set-INITIAL_FORMS and filterset_set-N-id for cloning.
    Both must be empty for cloning to work. But this should be possible on the server.
    OR just make a deep copy
    """
    
    # Assign form data if posted
    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    # if we got a view_id look if there is an according view
    if view_id:
        try:
            view_instance = View.objects.get(pk=view_id)
        except Exception, e:
            raise e
    else:
        view_instance = None

    # Create Forms and formsets
    view_form               = ViewForm(data=data, instance=view_instance)
    filter_set_formset      = FilterSetFormSet(data=data, instance = view_instance)

    if request.method == 'POST':
        valid = False
        if view_form.is_valid():
            if filter_set_formset.is_valid():
                valid = True

        if valid:
            view_instance = view_form.save()
            filter_set_formset.instance = view_instance
            filter_set_formset.save()
            messages.add_message(request, messages.SUCCESS, "Successfully saved.")
            return redirect("view_management")
        else:
            messages.add_message(request, messages.ERROR, "You are such a prick.")

    if request.method == 'GET':
        pass

    return render(request, 'myDmarcApp/view-editor.html', {
            'view_form'               : view_form,
            'filter_set_formset'      : filter_set_formset
        })

def delete(request, view_id):
    # XXX: Add try catch
    # XXX: Add ask confirm in Javascript
    View.objects.get(pk=view_id).delete()
    messages.add_message(request, messages.SUCCESS, "Successfully deleted view.")
    return redirect("view_management")

def export_svg(request, view_id):

    # Get data from client side via POST variables
    svg_data = request.POST.get("svg")

    document = xml.dom.minidom.parseString(svg_data)
    svg = document.documentElement

    # create svg
    svg_renderer = SvgRenderer()
    svg_renderer.render(svg)
    svg_rendered = svg_renderer.finish()
    pdf = renderPDF.drawToString(svg_rendered)

    # Response is file-like we can write pdf to it
    # XXX LP: Think of a proper filename like view title stripped + date
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "attachment; filename='somefilename.pdf'"
    response.write(pdf)     

    return response

def export_csv(request, view_id):
    view = View.objects.get(pk=view_id)

    csv_data = view.getCsvData()
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in csv_data),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response

def order(request):
    """Gets an orderd list of view ids. Calls OrderedModel static order method
    to save the order to view model. """
    
    try:
        view_ids = json.loads(request.body)
        print "view ids", view_ids
        views = []
        for view_id in view_ids:
            print view_id
            views.append(View.objects.get(pk=view_id))
        print "view objects", views
        OrderedModel.order(views)
        response = {"message" : "Successfully ordered views."}
        #messages.add_message(request, messages.SUCCESS, "Successfully ordered views.")
    except Exception, e:
        response = {"message" : "Could not order views."}

        #messages.add_message(request, messages.ERROR, "Ordering did not work.")
        raise e

    # XXX LP: Make nice ajax messages like in normal templates
    return HttpResponse(json.dumps(response), content_type="application/json")

"""
VIEW VIEWS END
"""
def view_management(request):
    return render(request, 'myDmarcApp/view-management.html', {'views' : View.objects.all()})

def deep_analysis(request, view_id = None):
    if view_id:
        view = View.objects.get(pk=view_id)
    else:
        view = View.objects.first()
    
    if not view:
        messages.add_message(request, messages.WARNING, "You should start creating views before you want to use them.")
        return redirect("view_management")

    sidebar_views        = View.objects.filter(enabled='true').values('id', 'title')
    # Only fetch querysets if they are displayed
    view_type_table_data = view.getTableData() if view.type_table else []
    view_type_line_data  = view.getLineData() if view.type_line else []
    view_type_map_data   = view.getMapData() if view.type_map else []

    return render(request, 'myDmarcApp/deep-analysis.html', {
            'sidebar_views'         : sidebar_views, 
            'the_view'              : view, 
            'view_type_table_data'  : view_type_table_data,
            'view_type_line_data'   : view_type_line_data,
            'view_type_map_data'    : view_type_map_data
        })

def help(request):
    return render(request, 'myDmarcApp/help.html', {})

