from django.urls import path
from . import views

urlpatterns = [
    path('initial/', views.initial_request, name='initial_request'),
    path('additional/', views.fill_additional_data, name='fill_additional_data'),
]
