from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from forms import *
from myDmarcApp.models import View, TimeFixed, TimeVariable

def index(request):
    return render(request, 'myDmarcApp/overview.html',{})

def edit(request):
    # f...form, fs...formset
    forms = {
        'f_view'                 : ViewForm(),
        'fs_time_variable'       : TimeVariableFormSet(),
        'fs_time_fixed'          : TimeFixedFormSet(),
        'fs_filter_set'          : FilterSetFormSet(),
        'fs_report_sender'       : ReportSenderFormSet(),
        'fs_report_recv'         : ReportReceiverDomainFormSet(),
        'fs_source_ip'           : SourceIPFormSet(),
        'fs_raw_dkim_domain'     : RawDkimDomainFormSet(),
        'fs_raw_dkim_result'     : RawDkimResultFormSet(),
        'fs_raw_spf_domain'      : RawSpfDomainFormSet(),
        'fs_raw_spf_result'      : RawSpfResultFormSet(),
        'fs_aligned_dkim_result' : AlignedDkimResultFormSet(),
        'fs_aligned_spf_result'  : AlignedSpfResultFormSet(),
        'fs_disposition'         : DispositionFormSet()
    }

    if request.method == 'POST':
        forms['f_view'] = ViewForm(request.POST)
        if forms.f_view.is_valid():
            view                = forms['f_view'].save(commit=False)
            view.save()

            # forms['fs_time_variable']           = TimeVariableFormSet(request.POST, instance=view)
            # forms['fs_time_fixed']              = TimeFixedFormSet(request.POST, instance=view)
            # forms['fs_time_variable']           =
            # forms['fs_time_fixed']                
            # forms['fs_filter_set']                
            # forms['fs_report_sender']             
            # forms['fs_report_recv']               
            # forms['fs_source_ip']             
            # forms['fs_raw_dkim_domain']               
            # forms['fs_raw_dkim_result']               
            # forms['fs_raw_spf_domain']                
            # forms['fs_raw_spf_result']                
            # forms['fs_aligned_dkim_result']               
            # forms['fs_aligned_spf_result']                
            # forms['fs_disposition']               
            return HttpResponse("Thanks beatch!")

    return render(request, 'myDmarcApp/view-editor.html', forms)

def deep_analysis(request, view_id='1'):
    views = View.objects.values('id', 'title')[:5]
    view =  View.objects.get(pk=view_id)
    # for f in View._meta.fields:
    #     print f.name, getattr(view, f.name, None)
    return render(request, 'myDmarcApp/deep-analysis.html',{'views': views, 'the_view': view})
