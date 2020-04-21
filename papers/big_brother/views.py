from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.template import loader
from .models import *
import qrcode

# CONSTANTS
BASE_URL = 'http://212.220.15.188:8000/'


@login_required
@csrf_protect
def bb_index(request): # TODO: После одобрения, либо отклонения отправляется письмо на почту о результате.
    if request.method == 'POST':
        query = request.POST
        user = query.get('user')
        req_id = query.get('req_id')
        decision = query.get('decision')
        comment = query.get('comment')
        if decision == 'Одобрить':
            status = 'Пропуск действителен'
        elif decision == 'Отклонить':
            status = 'Пропуск НЕ действителен'
        else:
            status = 'СТАТУС ПРОПУСКА НЕОПРЕДЕЛЕН'
        processed_car_request = Car_requests.objects.get(id=req_id)
        processed_car_request.status = decision
        try:
            car_pass = Car_passes.objects.get(car_id=processed_car_request.car_id)
            car_pass.status = status
            car_pass.moderator_comment = comment
        except Car_passes.DoesNotExist:
            car_pass = Car_passes.objects.create(
                company_id=processed_car_request.company_id,
                car_id=processed_car_request.car_id,
                req_id=processed_car_request,
                moderator=user,
                moderator_comment=comment,
                #pass_time= ,# TODO: Добавить срок действия пропуска
                status=status,
            )
        processed_car_request.save()
        car_pass.save()
        car_requests = Car_requests.objects.filter(status='В ожидании проверки')
        template = loader.get_template('big_brother/index.html')
        context = {'car_requests': car_requests,
                   'user': user,
                   'req_id': req_id,
                   'decision': decision,
                   'comment': comment,}
        return HttpResponse(template.render(context, request))
    if request.method == 'GET':
        car_requests = Car_requests.objects.filter(status='В ожидании проверки')
        template = loader.get_template('big_brother/index.html')
        context = {'car_requests': car_requests,}
        return HttpResponse(template.render(context, request))


@login_required
def accepted(request):
    if request.method == 'GET':
        car_requests = Car_requests.objects.filter(status='Одобрить')
        template = loader.get_template('big_brother/index.html')
        context = {'car_requests': car_requests,}
        return HttpResponse(template.render(context, request))


@login_required
def declined(request):
    if request.method == 'GET':
        car_requests = Car_requests.objects.filter(status='Отклонить')
        template = loader.get_template('big_brother/index.html')
        context = {'car_requests': car_requests,}
        return HttpResponse(template.render(context, request))


@login_required
def req_card(request, req_id):
    car_request = Car_requests.objects.get(id=req_id)
    try:
        car_pass = Car_passes.objects.get(req_id=req_id)
    except Car_passes.DoesNotExist:
        car_pass = 'DoesNotExist'
    template = loader.get_template('big_brother/req_card.html')
    context = {'req_id': req_id, 'car_request': car_request, 'car_pass': car_pass}
    return HttpResponse(template.render(context, request))


@login_required
def okveds_list(request):
    if request.method == 'POST':
        query = request.POST
        okved_id = query.get('okved_id')
        okved_name = query.get('okved_name')
        okved_description = query.get('okved_description')
        edited_okved = Okveds_list.objects.get(id=okved_id)
        edited_okved.okved_name = okved_name
        edited_okved.okved_description = okved_description
        edited_okved.save()
        okveds_list = Okveds_list.objects.all().order_by('okved_number')
        template = loader.get_template('big_brother/okveds_list.html')
        context = {'okveds_list': okveds_list}
        return HttpResponse(template.render(context, request))
    if request.method == 'GET':
        okveds_list = Okveds_list.objects.all().order_by('okved_number')
        template = loader.get_template('big_brother/okveds_list.html')
        context = {'okveds_list': okveds_list}
        return HttpResponse(template.render(context, request))


@login_required
def okved_card(request, okved_id):
    okved = Okveds_list.objects.get(id=okved_id)
    template = loader.get_template('big_brother/okved_card.html')
    context = {'okved': okved,}
    return HttpResponse(template.render(context, request))


def qr_gen(base_url, pass_id):
    url = f'{base_url}/?pass_id={pass_id}'
    return qrcode.make(url, box_size=8, border=1)