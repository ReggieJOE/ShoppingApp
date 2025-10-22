from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import admin_dashboard, user_order_history, order_history, customer_list, admin_product_detail, admin_products

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    path('products/', views.product_list, name='product_list'),
    path('products/category/<int:category_id>/', views.product_list, name='product_list_by_category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),

    # Admin Dashboard URLs
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/customers/', views.customer_list, name='customer_list'),
    path('dashboard/user/<int:user_id>/orders/', views.user_order_history, name='user_order_history'),
    path('dashboard/orders/', views.order_history, name='order_history'),
    path('dashboard/products/', views.admin_products, name='admin_products'),
    path('dashboard/products/<int:product_id>/', views.admin_product_detail, name='admin_product_detail'),
    path('dashboard/products/add/', views.admin_product_detail, name='admin_product_add'),
]