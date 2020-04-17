from django.db import models

# Create your models here.

from django.db import models
from django.utils.timezone import now


class Okveds_list(models.Model):
    """
    Таблица со списком окведов
    """
    okved_number = models.CharField(max_length=20, unique=True, null=False, default='')
    okved_name = models.TextField(unique=False, null=False, default='')
    okved_description = models.TextField(unique=False, null=True, default='')

    def __str__(self):
        return f'{self.okved_number}, {self.okved_name}'


class Okveds_allowed(models.Model):
    """
    Таблица со списком одобренных ОКВЕДов
    """
    okved_id = models.ForeignKey('Okveds_list', null=True, on_delete=models.SET)
    reason = models.CharField(max_length=150, null=False, unique=False,
                              default='Основания добавления данного ОКВЕД в список утвержденных не указаны')

    def __str__(self):
        return f'{self.okved_id}, {self.reason}'


class Legal_entities(models.Model):
    """
    Таблица с организациями.
    """
    inn = models.BigIntegerField(unique=True, null=False)
    org_name = models.CharField(max_length=150, unique=True, null=False,)
    owner_name = models.CharField(max_length=150, unique=True, null=False,)
    okved_id = models.ForeignKey('Okveds_list', null=True, on_delete=models.SET)
    tel = models.BigIntegerField(unique=False, null=False, default='+700000000000')
    email = models.EmailField(max_length=254, unique=False, null=False, default='none@email.debil')
    status = models.CharField(max_length=64, unique=False, null=False, default='Неизвестен')

    def __str__(self):
        return self.org_name


class Cars(models.Model):
    """
    Таблица с автомобилями организаций
    """
    l_e_id = models.ForeignKey('Legal_entities', null=True, on_delete=models.SET)
    pts_number = models.CharField(unique=True, max_length=15, null=False)
    license_plate = models.CharField(unique=True, max_length=9, null=False)
    brand = models.CharField(unique=False, max_length=64, null=False, default='Марка не указана')
    model = models.CharField(unique=False, max_length=64, null=False, default='Модель не указана')

    def __str__(self):
        return f'{self.license_plate}, {self.brand} {self.model}'


class L_e_requests(models.Model):
    """
    Список заявок организаций
    """
    l_e_id = models.ForeignKey('Legal_entities', null=True, on_delete=models.SET)
    car_id = models.ForeignKey('Cars', null=True, on_delete=models.SET)
    status = models.CharField(unique=False, max_length=64, default='В ожидании проверки')
    comment = models.CharField(unique=FileExistsError, max_length=256, default='Еще не обработана')

    def __str__(self):
        return f'{self.l_e_id}, {self.car_id} {self.status}'


class L_e_passes(models.Model):
    """
    Список пропусков для юридических лиц
    """
    l_e_id = models.ForeignKey('Legal_entities', null=True, on_delete=models.SET)
    car_id = models.ForeignKey('Cars', null=True, on_delete=models.SET)
    req_id = models.ForeignKey('L_e_requests', null=True, on_delete=models.SET)
    pass_time = models.DateField(unique=False, null=False, default=now)
    status = models.CharField(unique=False, max_length=64, default='Пропуск действителен')

    def __str__(self):
        return f'{self.req_id}, {self.status}'
