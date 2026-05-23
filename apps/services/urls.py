from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('', views.all_services_view, name='all_services'),
    path('<slug:slug>/', views.service_list_view, name='list'),
    path('<slug:slug>/create/', views.service_create_view, name='create'),
    path('<slug:slug>/<int:pk>/edit/', views.service_edit_view, name='edit'),
    path('<slug:slug>/<int:pk>/delete/', views.service_delete_view, name='delete'),
    path('<slug:slug>/categories/create/', views.category_create_view, name='category_create'),
    path('<slug:slug>/categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),
    path('<slug:slug>/categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
]
