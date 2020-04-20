from django.shortcuts import render

# Create your views here.

from big_brother.models import Okveds_list, Okveds_allowed, Companies, Cars, Car_requests, Car_passes
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_protect
from papers.configs import DADATA_API_KEY
import json
import requests


# CONSTS
DADATA_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"


def index(request):
    template = loader.get_template('slaves/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def reg_form(request):
    if request.method == 'GET':
        query = request.GET
        inputed_inn = query.get('inn')
        if inputed_inn == '' or not inputed_inn.isdigit():
            template = loader.get_template('slaves/index.html')
            context = {'alert': 'Неправильный ИНН!'}
            return HttpResponse(template.render(context, request))
        try:
            company = Companies.objects.get(inn=inputed_inn)
        except Companies.DoesNotExist:
            try:
                parsed_data = dadata_parser(inputed_inn)
            except:
                template = loader.get_template('slaves/index.html')
                context = {'alert': 'Неправильный ИНН!'}
                return HttpResponse(template.render(context, request))
            try:
                founded_okved_id = Okveds_list.objects.get(okved_number=parsed_data['okved'])
            except Okveds_list.DoesNotExist:
                founded_okved_id = Okveds_list.objects.create(okved_number=parsed_data['okved'],
                                                              okved_name='ДАННЫЕ ОТСУТСТВУЮТ! НЕОБХОДИМО ЗАПОЛНИТЬ!',
                                                              okved_description='ОПИСАНИЕ ОТСУТСТВУЕТ!')
            company = Companies.objects.create(inn=inputed_inn,
                                                    org_name=parsed_data['org_name'],
                                                    owner_name=parsed_data['owner_name'],
                                                    okved_id=founded_okved_id,
                                                    status=str(parsed_data['status']))
            company.save()
        template = loader.get_template('slaves/reg_form.html')
        context = {
            'debug_data': inputed_inn,
            'inn': inputed_inn,
            'company': company,
            'okved_status': okved_checker(company.okved_id)
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('slaves/index.html')
        context = {'alert': 'Здесь Вас не должно быть.'}
        return HttpResponse(template.render(context, request))


@csrf_protect
def reg_confirmed(request):
    if request.method == 'POST':
        query = request.POST
        inn = query.get('inn')
        tel = query.get('tel')
        email = query.get('email')
        pts_number = query.get('pts_number')
        license_plate_number = query.get('license_plate_number')
        license_plate_region = query.get('license_plate_region')
        license_plate = str(license_plate_number) + str(license_plate_region)
        brand = query.get('brand')
        model = query.get('model')
        comment = query.get('comment')
        company = Companies.objects.get(inn=inn)
        try:
            car = Cars.objects.get(license_plate=license_plate)
        except Cars.DoesNotExist:
            car = Cars.objects.create(company_id=company,
                                      pts_number=pts_number,
                                      license_plate=license_plate,
                                      brand=brand,
                                      model=model)
        try:
            car_request = Car_requests.objects.get(car_id=car)
            # TODO: Организовать логику проверки статуса заявки. Если пропуск действителен, то отправляем на главную и говорим, что пропуск на автомобиль действителен и выводим номер пропуска, если пропуск просрочен, то создаем новую заявку на пропуск, если бля там еще что-нибудь придумай нахуй.
        except Car_requests.DoesNotExist:
            car_request = Car_requests.objects.create(company_id=company,
                                                      car_id=car,
                                                      status='В ожидании проверки',
                                                      comment=comment)
        template = loader.get_template('slaves/reg_confirmed.html')
        context = {
            'debug_data': '',
            'inn': inn,
            'tel': tel,
            'email': email,
            'pts_number': pts_number,
            'license_plate': license_plate,
            'brand': brand,
            'model': model,
            'comment': comment
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('slaves/index.html')
        context = {'alert': 'Здесь Вас не должно быть.'}
        return HttpResponse(template.render(context, request))


def dadata_parser(inn):
    headers = {"Authorization": f"Token {DADATA_API_KEY}", "Content-Type": "application/json"}
    data = {'query': inn, 'count': 1}
    r = requests.post(url=DADATA_URL, data=json.dumps(data), headers=headers)
    recieved_data = r.json()
    org_name = recieved_data.get('suggestions')[0].get('value')
    okved = recieved_data.get('suggestions')[0].get('data').get('okved')
    if recieved_data.get('suggestions')[0].get('data').get('state').get('status') == 'ACTIVE':
        status = True
    else:
        status = False
    try:
        owner_name = recieved_data.get('suggestions')[0].get('data').get('management').get('name')
    except:
        owner_name = recieved_data.get('suggestions')[0].get('value')

    res = {'org_name': org_name, 'owner_name': owner_name, 'okved': okved, 'status': status}
    return res


def okved_checker(okved):
    try:
        obj = Okveds_allowed.objects.get(okved_id=okved)
        return 'full'
    except Okveds_allowed.DoesNotExist:
        try:
            obj = Okveds_allowed.objects.get(okved_id__icontains=okved)
            return 'half'
        except:
            return 'not'
