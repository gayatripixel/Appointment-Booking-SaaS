from django.urls import path

from . import views

app_name = 'shops'

urlpatterns = [

    # 🔥 API
    path('api/all-shops/', views.shops_list_api, name='all_shops_api'),

     # MY SHOP REDIRECT
    path('my-shop/', views.my_shop_redirect_view, name='my_shop'),

    path('setup/',views.shop_setup_view, name='shop_setup'),

    # 🔥 CUSTOMER SHOP LIST
    path('', views.shops_list_view, name='shops_list'),

    # 🔥 CUSTOMER PUBLIC PAGE (IMPORTANT)
    path('<slug:slug>/', views.shop_public_view, name='public'),

    # 🔥 OWNER DASHBOARD
    path('<slug:slug>/dashboard/', views.shop_dashboard_view, name='dashboard'),

    path('<slug:slug>/edit/', views.shop_edit_view, name='edit'),
    path('<slug:slug>/hours/', views.shop_hours_view, name='hours'),
    path('<slug:slug>/closures/', views.shop_closures_view, name='closures'),
    path('<slug:slug>/closures/<int:pk>/delete/', views.shop_closure_delete_view, name='closure_delete'),

    path('setup/', views.shop_setup_view, name='setup'),


    path('', views.shops_list_view, name='list'),

]
