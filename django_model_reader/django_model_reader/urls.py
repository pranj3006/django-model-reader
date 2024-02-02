from django.contrib import admin
from django.urls import path, include
from . import views
app_name='django_model_reader'
urlpatterns = [
    path('view_models_list/', views.view_models_list, name='view_models_list'),
    path('get_models_data/', views.get_models_data, name='get_models_data'),
]
