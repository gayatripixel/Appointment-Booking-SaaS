from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_shop_select_view, name='shop_select'),
    path('<slug:slug>/', views.staff_list_view, name='list'),
    path('<slug:slug>/add/', views.staff_create_view, name='create'),
    path('<slug:slug>/<int:pk>/edit/', views.staff_edit_view, name='edit'),
    path('<slug:slug>/<int:pk>/delete/', views.staff_delete_view, name='delete'),
    path('<slug:slug>/<int:pk>/services/', views.staff_services_view, name='services'),
    path('<slug:slug>/<int:pk>/hours/', views.staff_hours_view, name='hours'),
    path('<slug:slug>/<int:pk>/time-off/', views.staff_time_off_view, name='time_off'),
    path('<slug:slug>/<int:pk>/time-off/<int:time_off_pk>/delete/', views.staff_time_off_delete_view, name='time_off_delete'),
]
