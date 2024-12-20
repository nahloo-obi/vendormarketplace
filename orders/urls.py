from django.urls import path, include
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name="place_order"),
    path('payments/', views.payments, name="payments"),
    path('order-complete/', views.order_complete_paypal, name='order_complete'),


    #stripe payment
    path('create-checkout-session/', views.create_checkout_session_view, name="create-checkout-session"),
    path('payment-cancel/', views.paymentCancel, name="payment_cancel"),
    path('webhook/stripe/', views.my_webhook_view, name="webhook-stripe"),

  

]