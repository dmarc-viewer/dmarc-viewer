from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from forms import *
from myDmarcApp.models import View, TimeFixed, TimeVariable
from django.contrib import messages

def index(request):
    return render(request, 'myDmarcApp/overview.html',{})

def edit(request, view_id = None):
    # Retrieve All views for sidebar
    sidebar_views = View.objects.values('id', 'title')
    
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

    # if we got a view assign it to the form
    try:
        view_time_variable_instance = view_instance.timevariable
    except Exception, e:
        view_time_variable_instance = None
    try:
        view_time_fixed_instance = view_instance.timefixed
    except Exception, e:
        view_time_fixed_instance = None


    # Create Forms and formsets
    view_time_variable_form  = TimeVariableForm(data=data, instance=view_time_variable_instance)
    view_time_fixed_form     = TimeFixedForm(data=data, instance=view_time_fixed_instance)
    view_form                = ViewForm(data=data, instance=view_instance, 
                                        time_variabe_form = view_time_variable_form, 
                                        time_fixed_form = view_time_fixed_form)

    # filter_set_formset      = FilterSetFormSet(data)
         
    filter_formsets = {
        # 'report_sender'       : ReportSenderFormSet(data),
        # 'report_recv'         : ReportReceiverDomainFormSet(data),
        # 'source_ip'           : SourceIPFormSet(data),
        # 'raw_dkim_domain'     : RawDkimDomainFormSet(data),
        # 'raw_dkim_result'     : RawDkimResultFormSet(data),
        # 'raw_spf_domain'      : RawSpfDomainFormSet(data),
        # 'raw_spf_result'      : RawSpfResultFormSet(data),
        # 'aligned_dkim_result' : AlignedDkimResultFormSet(data),
        # 'aligned_spf_result'  : AlignedSpfResultFormSet(data),
        # 'disposition'         : DispositionFormSet(data)
    }

    if request.method == 'POST':
        valid = False
        if view_form.is_valid():
            valid = True            
    #             # FILTER SET STUFF
    #             # if filter_set_formset.is_valid():
    #             #     filter_set_formset.instance = view
    #             #     filter_set = filter_set_formset.save()

    #                 # for key, value in filter_formsets.iteritems():
    #                 #     for i in range(len(filter_set)):
    #                 #         filter_formsets[key][i].instance = filter_set[i]
    #                 #     filter_formsets[key].save()

    #         valid = True

        if valid:
            view_instance = view_form.save()

            messages.add_message(request, messages.SUCCESS, 'Successfully saved!')
        else:
            messages.add_message(request, messages.ERROR, 'You are such a brick!')

    if request.method == 'GET':
        pass

    return render(request, 'myDmarcApp/view-editor.html', {
            'sidebar_views'           : sidebar_views,
            'view_form'               : view_form,
            'view_time_variable_form' : view_time_variable_form,
            'view_time_fixed_form'    : view_time_fixed_form,
            # 'filter_set_formset'      : filter_set_formset,
            # 'filter_formsets'         : filter_formsets
        })

def deep_analysis(request, view_id = None):
    if not view_id:
        view_id = View.objects.values('id')[0]['id']
    sidebar_views = View.objects.values('id', 'title')
    view =  View.objects.get(pk=view_id)
    # for f in View._meta.fields:
    #     print f.name, getattr(view, f.name, None)
    return render(request, 'myDmarcApp/deep-analysis.html', {'sidebar_views': sidebar_views, 'the_view': view})
