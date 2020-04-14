from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render


# Create your views here.
def index(request):
    template = loader.get_template('slaves/index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def reg_form(request):
    template = loader.get_template('slaves/reg_form.html')
    context = {}
    return HttpResponse(template.render(context, request))