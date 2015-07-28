from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from forms import *
from myDmarcApp.models import View, TimeFixed, TimeVariable
from django.contrib import messages

def index(request):
    return render(request, 'myDmarcApp/overview.html',{})

def edit(request):
    # f...form, fs...formset
    
    if request.method == 'POST':
        data = request.POST
    else:
        data = None


    view_form           = ViewForm(data)

    view_formsets       = {
        'time_variable'       : TimeVariableFormSet(data),
        'time_fixed'          : TimeFixedFormSet(data),

    }
    filter_set_formset     = FilterSetFormSet(data)

    filter_formsets = {
        'report_sender'       : ReportSenderFormSet(data),
        'report_recv'         : ReportReceiverDomainFormSet(data),
        'source_ip'           : SourceIPFormSet(data),
        'raw_dkim_domain'     : RawDkimDomainFormSet(data),
        'raw_dkim_result'     : RawDkimResultFormSet(data),
        'raw_spf_domain'      : RawSpfDomainFormSet(data),
        'raw_spf_result'      : RawSpfResultFormSet(data),
        'aligned_dkim_result' : AlignedDkimResultFormSet(data),
        'aligned_spf_result'  : AlignedSpfResultFormSet(data),
        'disposition'         : DispositionFormSet(data)
    }

    if request.method == 'POST':
        if view_form.is_valid():
            view = view_form.save()

            for key, value in view_formsets.iteritems():
                # Validate
                view_formsets[key].instance = view
                view_formsets[key].save()
            
            # FILTER SET STUFF
            if filter_set_formset.is_valid():
                filter_set_formset.instance = view
                filter_set = filter_set_formset.save()

                for key, value in filter_formsets.iteritems():

                    for i in range(len(filter_set)):
                        if key == raw_dkim_domain:
                            print filter_formsets[key][i].value
                        filter_formsets[key][i].instance = filter_set[i]
                        print filter_formsets[key][i].instance
                    filter_formsets[key].save()

            messages.add_message(request, messages.SUCCESS, 'Successfully saved!')
        else:
            messages.add_message(request, messages.ERROR, 'You are such a brick!')


    return render(request, 'myDmarcApp/view-editor.html', {
            'view_form'             : view_form,
            'view_formsets'         : view_formsets,
            'filter_set_formset'    : filter_set_formset,
            'filter_formsets'       : filter_formsets
        })

def deep_analysis(request, view_id = None):
    if not view_id:
        view_id = View.objects.values('id')[0]['id']
    views = View.objects.values('id', 'title')
    view =  View.objects.get(pk=view_id)
    # for f in View._meta.fields:
    #     print f.name, getattr(view, f.name, None)
    return render(request, 'myDmarcApp/deep-analysis.html',{'views': views, 'the_view': view})
