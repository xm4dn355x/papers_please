from django.shortcuts import render

# Create your views here.

from big_brother.models import Okveds_list, Okveds_allowed, Companies, Cars, Car_requests, Car_passes
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_protect


def search_id(request):
    if request.method == 'GET':
        query = request.GET
        pass_id = query.get('pass_id')
        try:
            car_pass = Car_passes.objects.get(id=pass_id)
        except Car_passes.DoesNotExist:
            car_pass = 'error'
        template = loader.get_template('gestapo/g_index.html')
        context = {'car_pass': car_pass,}
        return HttpResponse(template.render(context, request))


def search_lp(request):
    if request.method == 'GET':
        query = request.GET
        lp = query.get('lp')
        try:
            car = Cars.objects.get(license_plate=lp)
            car_pass = Car_passes.objects.get(car_id=car.id)
        except Car_passes.DoesNotExist:
            car_pass = 'error'
        except Cars.DoesNotExist:
            car_pass = 'error'
        template = loader.get_template('gestapo/g_index.html')
        context = {'car_pass': car_pass,}
        return HttpResponse(template.render(context, request))
