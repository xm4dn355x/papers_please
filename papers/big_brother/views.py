# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.

from .models import *
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.template import loader
from io import BytesIO, StringIO
from papers.configs import DJANGO_EMAIL_HOST_USER
import base64
import qrcode
from xhtml2pdf import pisa
from weasyprint import HTML, CSS
import pdfkit
from datetime import datetime


# CONSTANTS
BASE_URL = 'http://212.220.15.188:8000/pass/'


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
            send_pass_to_mail(car_pass, request, 'Cтатус Вашегшо пропуска изменился',
                              f'Текущий статус Вашего пропуска: {status}')
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
            send_pass_to_mail(car_pass, request, f'Вам выдан пропуск со статусом: {status}',
                              f'Направляем Вам пропуск для Вашего автомобиля в прикрепленном PDF документе\n'
                              f'Текущий статус Вашего пропуска: {status}\n\n'
                              f'Для удобства использования пропуска распечатайте прикрепленный документ, '
                              f'а так же вы можете предъявлять его с экрана Вашего мобильного телефона.')
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
        okved_number = query.get('okved_number')
        okved_name = query.get('okved_name')
        okved_description = query.get('okved_description')
        if 'delete' in query:
            instance = Okveds_list.objects.get(id=okved_id)
            instance.delete()
        else:
            edited_okved = Okveds_list.objects.get(id=okved_id)
            edited_okved.okved_number = okved_number
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


@login_required
def create_okved(request):
    if request.method == 'POST':
        query = request.POST
        okved_number = query.get('okved_number')
        okved_name = query.get('okved_name')
        okved_description = query.get('okved_description')
        try:
            okved = Okveds_list.objects.get(okved_number=okved_number)
            okved.okved_name = okved_name
            okved.okved_description = okved_description
            okved.save()
        except Okveds_list.DoesNotExist:
            okved = Okveds_list.objects.create(okved_number=okved_number,
                                               okved_name=okved_name,
                                               okved_description=okved_description)
            okved.save()
        okveds_list = Okveds_list.objects.all().order_by('okved_number')
        template = loader.get_template('big_brother/okveds_list.html')
        context = {'okveds_list': okveds_list}
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('big_brother/okved_card.html')
        context = { 'create': True }
        return HttpResponse(template.render(context, request))


def send_pass_to_mail(car_pass, request, message_subject, message_body):
    print('send_pass_to_email begin')
    pdf_gen(car_pass, request)
    email_message = EmailMessage(
        subject=message_subject,
        body=message_body,
        from_email=DJANGO_EMAIL_HOST_USER,
        to=(car_pass.company_id.email,),
        # attachments=[(f'Пропуск {car_pass.car_id.license_plate}.pdf', pdf, 'application/pdf')]
    )
    with open('out.pdf', 'rb') as f:
        email_message.attach(f"Пропуск {car_pass.car_id.license_plate}.pdf", f.read(), "application/pdf")
    print(f'email_message object {email_message}')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    email_message.send(fail_silently=False)
    print('email message sended')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('send_pass_to_email end')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')



def pdf_gen(car_pass, request):
    # print('pdf_gen begin')
    # template = loader.get_template('big_brother/pdf.html')
    # context = {'pass_id': car_pass.id,
    #            'company_name': car_pass.company_id.org_name,
    #            'brand': car_pass.car_id.brand,
    #            'model': car_pass.car_id.model,
    #            'license_plate': car_pass.car_id.license_plate,
    #            'qr': qr_gen(BASE_URL, car_pass.id)}
    # html = template.render(context, request)
    # pdf = HTML(string=html).write_pdf()
    template = loader.get_template('big_brother/pdf.html')
    try:
        car_pass = Car_passes.objects.get(id=car_pass.id)
    except Car_passes.DoesNotExist:
        car_pass = 'error'
    context = {'pass_id': car_pass.id,
               'company_name': car_pass.company_id.org_name,
               'brand': car_pass.car_id.brand,
               'model': car_pass.car_id.model,
               'license_plate': car_pass.car_id.license_plate,
               'qr': qr_gen(BASE_URL, car_pass.id)}
    html = template.render(context, request)
    options = {
        'page-size': 'A5',
        'margin-top': '1cm',
        'margin-right': '1cm',
        'margin-bottom': '1cm',
        'margin-left': '1cm',
        'encoding': "UTF-8",
        'zoom': 1.25,
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'no-outline': None
    }
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_string(html, 'out.pdf', options=options, configuration=config)



def qr_gen(base_url, pass_id):
    url = f'{base_url}?pass_id={pass_id}'
    qr = qrcode.make(url, box_size=10, border=0)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer_img = buffer.getvalue()
    res = f"""data:image/jpeg;base64,{str(base64.b64encode(buffer_img)).replace("b'", "").replace("'", "")}"""
    return res


def pass_testing(request):
    stime = datetime.now()
    template = loader.get_template('big_brother/pdf.html')
    pass_id = 17
    try:
        car_pass = Car_passes.objects.get(id=pass_id)
    except Car_passes.DoesNotExist:
        car_pass = 'error'
    context = {'pass_id': car_pass.id,
               'company_name': car_pass.company_id.org_name,
               'brand': car_pass.car_id.brand,
               'model': car_pass.car_id.model,
               'license_plate': car_pass.car_id.license_plate,
               'qr': qr_gen(BASE_URL, 17)}
    html = template.render(context, request)
    options = {
        'page-size': 'A5',
        'margin-top': '1cm',
        'margin-right': '1cm',
        'margin-bottom': '1cm',
        'margin-left': '1cm',
        'encoding': "UTF-8",
        'zoom': 1.25,
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'no-outline': None
    }
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = pdfkit.from_string(html, 'out.pdf', options=options, configuration=config)
    with open('out.pdf', 'rb') as file_pdf:
        response = HttpResponse(file_pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="home_page.pdf"'
    time_delta = datetime.now() - stime
    print(f'Время генерации PDF = {time_delta}')
    return response