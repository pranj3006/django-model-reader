from django.shortcuts import render
from django_model_reader.model_reader_service import  ModelReaderService
from django.http import HttpResponse
from django.http import JsonResponse
# Create your views here.


def get_models_data(request):
    serv_mdreader = ModelReaderService()
    schema_data = serv_mdreader.get_all_models()
    
    return JsonResponse(schema_data,status=200)

def view_models_list(request):
    serv_mdreader = ModelReaderService()
    schema_data = serv_mdreader.get_all_models()
    context = {
        'title': 'Database Schema Visualization',
        'schema_data': schema_data,
    }
    return render(request, 'schema_visualization.html', context)
