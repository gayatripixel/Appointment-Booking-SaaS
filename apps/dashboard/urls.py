from django.urls import path

from . import views

from .views import create_checkout_session
from django.urls import path

from .views import (
    create_checkout_session,
    payment_success,
    payment_cancel
)

app_name = 'dashboard'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('services/', views.services_view, name='services'),
    path('staff/', views.staff_view, name='staff'),
    path('customers/', views.customers_view, name='customers'),
    path("api/", views.dashboard_data, name="dashboard-api"),
    path("reports/", views.reports_view, name="reports"),
    
    path(
         'subscribe/<str:plan>/',
         create_checkout_session,
         name='subscribe'
    ),
    path(
         'payment-success/',
          payment_success,
         name='payment_success'
    ),

    path(
         'payment-cancel/',
         payment_cancel,
         name='payment_cancel'
    ),

     path(
        "services/<int:service_id>/edit/",
        views.service_edit,
        name="service_edit",
    ),

    path('services/delete/<int:service_id>/',
         views.service_delete,
         name='service_delete'
     ),

    path("services/add/",
          views.service_add,
            name="service_add"
          ),

     path('notifications/',
          views.notifications_view,
         name='notifications'
     ),
]
