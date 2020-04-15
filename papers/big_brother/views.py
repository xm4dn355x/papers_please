from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader


def bb_index(request):
    template = loader.get_template('big_brother/index.html')
    context = {}
    return HttpResponse(template.render(context, request))