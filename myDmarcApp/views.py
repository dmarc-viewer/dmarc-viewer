from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from forms import *
from myDmarcApp.models import View, TimeFixed, TimeVariable
from django.contrib import messages
import json 

def index(request):
    return render(request, 'myDmarcApp/overview.html',{})

def edit(request, view_id = None, clone = False):
    
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

            messages.add_message(request, messages.SUCCESS, 'Successfully saved!')
            return redirect("view_management")

        else:
            messages.add_message(request, messages.ERROR, 'You are such a prick!')

    if request.method == 'GET':
        pass

    return render(request, 'myDmarcApp/view-editor.html', {
            'view_form'               : view_form,
            'filter_set_formset'      : filter_set_formset,
            'clone'                   : clone
        })

def delete_view(request, view_id):
    # XXX: Add try catch
    # XXX: Add ask confirm in Javascript
    View.objects.get(pk=view_id).delete()
    messages.add_message(request, messages.SUCCESS, 'Successfully deleted view!')
    return redirect("view_management")


def deep_analysis(request, view_id = None):
    if not view_id:
        view_id = View.objects.values('id')[0]['id']

    sidebar_views        = View.objects.values('id', 'title')
    view                 = View.objects.get(pk=view_id)
    filter_set_data_list = view.getData()

    """
    View Type Line
    x: time bins
        with variable sizes. we define how many datapoints
    y: message count per bin

    labels :
        date_range_begin - date_range_end | absolute_begin(time_variable) - absolute_end(time_variable)
        given n wanted points on the x scale
        we have to divide the x scale in n equal bins and find a name (one of day, week, month) for each bin

    datasets:
        for each data_set (by filter_set)
            color:  hex to rgba
            data:   sum(Record.count aggregated by bin)
    """

    view_type_line_data = json.dumps({ 
        'labels'    : ["January", "February", "March", "April", "May", "June", "July"],
        'datasets' : [
                {
                    'label'           : "My First dataset",
                    'strokeColor': "rgba(220,220,220,1)",
                    'pointColor': "rgba(220,220,220,1)",
                    'pointStrokeColor': "#fff",
                    'pointHighlightFill': "#fff",
                    'pointHighlightStroke': "rgba(220,220,220,1)",
                    'data'            :[65, 59, 80, 81, 56, 55, 40]
                }
        ]
    }) 

    return render(request, 'myDmarcApp/deep-analysis.html', {
            'sidebar_views'         : sidebar_views, 
            'the_view'              : view, 
            'filter_set_data_list'  : filter_set_data_list,
            'view_type_line_data'   : view_type_line_data
        })

def view_management(request):
    return render(request, 'myDmarcApp/view-management.html', {'views' : View.objects.all()})

def help(request):
    return render(request, 'myDmarcApp/help.html', {})

