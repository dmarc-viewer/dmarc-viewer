from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from forms import *

def index(request):
    return render(request, 'myDmarcApp/overview.html',{})

def edit(request):
    # f...form, fs...formset
    f_view              = ViewForm()
    fs_time_variable    = TimeVariableFormSet()
    fs_time_fixed       = TimeFixedFormSet()
    
    if request.method == 'POST':
        f_view = ViewForm(request.POST)
        if f_view.is_valid():
            view             = f_view.save(commit=False)
            fs_time_variable = TimeVariableFormSet(request.POST, instance=view)
            fs_time_fixed    = TimeFixedFormSet(request.POST, instance=view)

            if fs_time_variable.is_valid() and fs_time_fixed.is_valid():
                view.save()
                fs_time_variable.save()
                fs_time_fixed.save()
                return HttpResponse("Thanks beatch.")

    return render(request, 'myDmarcApp/view-editor.html', {'f_view'           : f_view, 
                                                           'fs_time_variable' : fs_time_variable,
                                                           'fs_time_fixed'    : fs_time_fixed})
