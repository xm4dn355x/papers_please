from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader


def test_index(request):
    template = loader.get_template('fronttesting/test_index.html')
    context = {}
    return HttpResponse(template.render(context, request))