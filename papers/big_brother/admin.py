from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Okveds_list, Okveds_allowed, Companies, Cars, Car_requests, Car_passes


admin.site.register(Okveds_list)
admin.site.register(Okveds_allowed)
admin.site.register(Companies)
admin.site.register(Cars)
admin.site.register(Car_requests)
admin.site.register(Car_passes)
