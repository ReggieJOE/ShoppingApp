from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ========== MAIN SITE URLS ==========
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/category/<int:category_id>/', views.product_list, name='product_list_by_category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),

    # ========== ADMIN URLS ==========
    # Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Products Management
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/add/', views.admin_product_edit, name='admin_product_add'),
    path('admin/products/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
    path('admin/products/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),

    # Customers Management
    path('admin/customers/', views.customer_list, name='customer_list'),
    path('admin/customers/<int:user_id>/orders/', views.user_order_history, name='user_order_history'),

    # Orders Management
    path('admin/orders/', views.order_history, name='order_history'),
    path('manage/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),

    path('manage/categories/', views.admin_categories, name='admin_categories'),
    path('manage/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),

]
