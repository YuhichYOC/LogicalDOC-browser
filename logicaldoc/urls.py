from django.urls import path

from . import views

app_name = 'logicaldoc'
urlpatterns = [
    path('', views.browse, name='index'),
]
