from django.http import HttpResponse, JsonResponse
from django.urls import reverse
import simplejson as json # type: ignore
from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount
from marketplace.views import is_ajax
from .forms import OrderForm
from .models import Order, Payment, OrderedItem
from .utils import generate_order_number
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os


#stripe payment
import stripe # type: ignore
stripe.api_key = settings.STRIPE_SECRET_KEY_TEST


# Create your views here.
@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user= request.user.pk).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <=0:
        return redirect('marketplace')
    
    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    sum_total = get_cart_amount(request)['sum_total']
    tax_data = get_cart_amount(request)['tax_dict']
    print(tax_data)

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.total = sum_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.user = request.user           
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()

            context ={
                'order': order,
                'cart_items': cart_items
            }
            return render(request, 'orders/place_order.html', context)

        else:
            print(form.errors)

    return render(request, 'orders/place_order.html')



#paypal payment
@login_required(login_url='login')
def payments(request):


    if is_ajax(request=request) and request.method == "POST":
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        user = request.user

        response = payment_gateway_handler(order_number, transaction_id, payment_method, status)
        response_content = json.loads(response.content)
        return JsonResponse(response_content)

        

def order_complete_paypal(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    
    try:
        # order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        order = Order.objects.get(user = request.user, order_number=order_number, is_ordered=True)
        
        ordered_item = OrderedItem.objects.filter(order=order)

        sub_total = 0
        for item in ordered_item:
            sub_total += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
    
        context = {
            'order': order,
            'ordered_item': ordered_item,
            'sub_total': sub_total,
            'tax_data': tax_data,
        }
        
        return render(request, 'orders/order_complete.html', context)
    except Exception as e:
        print(f"failed order: {e}")

        return redirect('home')
    
def payment_gateway_handler(order_number, transaction_id, payment_method, status):

    try:
        order = Order.objects.get(order_number=order_number)

        payment = Payment(user=order.user, transaction_id=transaction_id, payment_method=payment_method, amount=order.total, status=status)

        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.status = "Completed"
        order.save()
       
        cart_items = Cart.objects.filter(user=order.user)

        for item in cart_items:
            ordered_item = OrderedItem()
            ordered_item.order = order
            ordered_item.payment = payment
            ordered_item.user = order.user
            ordered_item.storeitem= item.item
            ordered_item.quantity = item.quantity
            ordered_item.price = item.item.price
            ordered_item.amount = item.item.price * item.quantity

            ordered_item.save()

        mail_subject = "Thank you for ordering from our store"
        mail_template = "orders/order_confirmation_email.html"

        context ={
            'user': order.user,
            'order': order,
            'to_email': order.email
        }

        #send notification to customers
        send_notification(mail_subject, mail_template, context)


        #send notification to vendors
        mail_subject = "You have received a new Order!!! "
        mail_template = "orders/new_order_received.html"
        to_emails = []

        for item in cart_items:
            if item.item.vendor.user.email not in to_emails:
                to_emails.append(item.item.vendor.user.email)

        context ={
            'order': order,
            'to_email': to_emails,
        }
        send_notification(mail_subject, mail_template, context)

        #cart_items.delete()

        response = {
            'order_number': order_number,
            'transaction_id': transaction_id
        }

        return JsonResponse(response)
  
    
    except Exception as e:
        print(f"error{e}")
        return HttpResponse("Error")
    
    

def create_checkout_session_view(request):
    order_complete = "orders/order-complete/"
    base_url = os.getenv('BASE_URL', 'http://127.0.0.1:8000')

    if request.method == "POST":
        order_id = request.POST.get("order")
        sum_total = request.POST.get("total")
        order_number = request.POST.get('order_number')


        order = Order.objects.get(id=order_id)
        
        try:
            host = request.get_host()
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types = ['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount':  int(float(sum_total)) * 100,
                            'product_data':{
                                'name': order_number,
                                
                            }
                        },
                        'quantity' : 1,
                        

                    }
                ],

                mode='payment',
                
                success_url = f"{base_url}/{order_complete}?order_no={order_number}&trans_id={{CHECKOUT_SESSION_ID}}",

                cancel_url="http://{}{}".format(host, reverse('payment_cancel')),
            )

            return redirect(checkout_session.url, code=303)
        
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")


    return HttpResponse("ERROR")

def paymentCancel(request):
    context = {
        'payment_success': 'cancel'
    }
    return render(request, 'orders/confirmation.html', context)



@csrf_exempt
def my_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  if (
    event['type'] == 'checkout.session.completed'
    or event['type'] == 'checkout.session.async_payment_succeeded'
  ):
    
    session = event['data']['object']

    session_id = session['id']  # PaymentIntent ID
    payment_intent = session['payment_intent']
    line_items = stripe.checkout.Session.list_line_items(session_id)
    payment_method = 'Stripe'
    status = 'Completed'

    order_number = line_items['data'][0]['description']

    response = payment_gateway_handler(order_number, payment_intent, payment_method, status)

    # response_content = json.loads(response.content)

    # base_url = os.getenv('BASE_URL', 'http://127.0.0.1:8000')

    # order_complete = "orders/order-complete/"
    # redirect_url = f"{base_url}/{order_complete}?order_no={order_number}&trans_id={payment_intent}"
    
 
    

  return HttpResponse(status=200)

