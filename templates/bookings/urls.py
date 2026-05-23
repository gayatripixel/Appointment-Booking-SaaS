from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('<slug:slug>/<int:service_id>/', views.booking_create_view, name='create'),
]