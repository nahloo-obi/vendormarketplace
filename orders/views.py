from django.http import HttpResponse, JsonResponse
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

@login_required(login_url='login')
def payments(request):


    if is_ajax(request=request) and request.method == "POST":
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)

        payment = Payment(user=request.user, transaction_id=transaction_id, payment_method=payment_method, amount=order.total, status=status)

        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()
       
        cart_items = Cart.objects.filter(user=request.user)

        for item in cart_items:
            ordered_item = OrderedItem()
            ordered_item.order = order
            ordered_item.payment = payment
            ordered_item.user = request.user
            ordered_item.storeitem= item.item
            ordered_item.quantity = item.quantity
            ordered_item.price = item.item.price
            ordered_item.amount = item.item.price * item.quantity

            ordered_item.save()

        mail_subject = "Thank you for ordering from our store"
        mail_template = "orders/order_confirmation_email.html"

        context ={
            'user': request.user,
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


        #cart_items.delete()

        response = {
            'order_number': order_number,
            'transaction_id': transaction_id
        }

        return JsonResponse(response)
  
    return HttpResponse("Payments View")


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    
    try:
        print('inside order complete')
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
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
    
