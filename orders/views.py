from django.http import HttpResponse
import simplejson as json # type: ignore
from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount
from marketplace.views import is_ajax
from .forms import OrderForm
from .models import Order
from .utils import generate_order_number

# Create your views here.

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


def payments(request):
    if is_ajax(request=request) and request.method == "POST":
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
    

    return HttpResponse("Payments View")