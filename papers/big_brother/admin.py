from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Okveds_list, Okveds_allowed, Legal_entities, Cars, L_e_requests, L_e_passes


admin.site.register(Okveds_list)
admin.site.register(Okveds_allowed)
admin.site.register(Legal_entities)
admin.site.register(Cars)
admin.site.register(L_e_requests)
admin.site.register(L_e_passes)
