from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('select-category/', views.select_category_view, name='select-category'),
    path('skincare-dashboard/', views.skincare_dashboard_view, name='skincare-dashboard'),
    path('haircare-dashboard/', views.haircare_dashboard_view, name='haircare-dashboard'),
    path('haircare-products/', views.haircare_products_views, name='haircare-products'),
    path('admin-dashboard/', views.admin_main_dashboard, name='admin-dashboard'),
    path('skincare-products/', views.skincare_recommendation_view, name='skincare-products'),
]