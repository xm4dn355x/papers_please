"""slaves URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.bb_index, name='bb_index'),
    path('req_card/?req_id=<int:req_id>', views.req_card, name='req_card'),
    path('accepted/', views.accepted, name='accepted'),
    path('declined/', views.declined, name='declined'),
    path('okveds_list', views.okveds_list, name='okveds_list'),
    path('create_okved', views.create_okved, name='create_okved'),
    path('okved_card/?okved_id=<int:okved_id>', views.okved_card, name='okved_card'),
    # path('pass_testing', views.pass_testing, name='pass_testing')
]