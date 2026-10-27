from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('units/', views.unit_list_view, name='unit_list'),
    path('availability/', views.availability_view, name='availability'),
    path('reserve/', views.reserve_view, name='reserve'),
    path('list/', views.reservation_list_view, name='reservation_list'),
    path('cancel/<str:reservation_id>/', views.cancel_view, name='cancel_reservation'),
]
