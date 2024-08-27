
from django.urls import path
from . import views
from MyApp import views


urlpatterns = [
    path('', views.login, name='login'),
    path('index', views.index, name='index'),
    path('login/', views.admin_login, name='admin_login'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),

    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/dashboard/charts.html', views.charts, name='charts'),
    path('seller/dashboard/manage-users/', views.manage_users, name='manage_users'),
    path('seller/dashboard/manage-users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('seller/dashboard/manage-users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('seller/dashboard/manage-products/', views.manage_product, name='manage_products'),
    path('seller/dashboard/manage-products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/dashboard/manage-products/add/', views.add_product, name='add_product'),
    path('place_order/', views.place_order, name='place_order'),
    path('seller/dashboard/orders/', views.seller_orders, name='seller_orders'),
    path('seller/dashboard/orders/update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),

    path('seller/dashboard/manage-products/delete/<int:product_id>/', views.delete_product, name='delete_product'),


    
]

#path("signup/", views.authView, name="authView"),