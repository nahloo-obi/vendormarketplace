from django.urls import path, include
from . import views
from accounts import views as AccountViews


urlpatterns = [
    path('', AccountViews.customerDashboard, name='customer'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('my-orders/', views.my_orders, name='customer_my_orders'),
    path('order-details/<int:order_number>/', views.order_details, name='order_details')
]