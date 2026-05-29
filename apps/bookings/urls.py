from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [

    #  path('create/<slug:slug>/', views.create_booking, name='create'),

    # Customer booking flow (public)
    path('<slug:slug>/book/', views.booking_start_view, name='start'),
    path('<slug:slug>/book/<int:service_pk>/staff/', views.booking_staff_view, name='staff'),
    path('<slug:slug>/book/<int:service_pk>/datetime/', views.booking_datetime_view, name='datetime'),
    path('<slug:slug>/book/<int:service_pk>/confirm/', views.booking_confirm_view, name='confirm'),
    path('<slug:slug>/book/<int:pk>/success/', views.booking_success_view, name='success'),

    # Shop owner management
    path('<slug:slug>/manage/', views.booking_list_view, name='manage_list'),
    path('<slug:slug>/manage/create/', views.booking_create_view, name='manage_create'),
    path('<slug:slug>/manage/<int:pk>/', views.booking_detail_view, name='manage_detail'),
    path('<slug:slug>/manage/<int:pk>/status/', views.booking_status_view, name='manage_status'),
    path('<slug:slug>/manage/<int:pk>/cancel/', views.booking_cancel_view, name='manage_cancel'),

    # Customer's own bookings
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('my-bookings/<int:pk>/cancel/', views.my_booking_cancel_view, name='my_booking_cancel'),

    # API / HTMX endpoints
    path('<slug:slug>/api/slots/', views.slots_api_view, name='api_slots'),


    path(
    '<slug:slug>/book/<int:service_pk>/checkout/',
    views.create_booking_checkout,
    name='create_booking_checkout'
),

path(
    '<slug:slug>/payment/success/',
    views.booking_payment_success,
    name='booking_payment_success'
),

path(
    '<slug:slug>/payment/cancel/',
    views.booking_payment_cancel,
    name='booking_payment_cancel'
),

path('followup/add/', views.add_followup_view, name='add_followup'),


  
]


