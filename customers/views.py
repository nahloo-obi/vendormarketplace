from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages
from orders.models import Order, OrderedItem
import json

# Create your views here.


@login_required(login_url='login')
def customer_profile(request):
    profile = get_object_or_404(UserProfile, user = request.user.pk)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile Updated')
            return redirect('customer_profile')
        else:
            print(profile_form.errors)
            print(user_form.errors)

    else:

        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form': profile_form,
        'user_form' : user_form,
        'profile': profile,
    }

    return render(request, 'customers/customer_profile.html', context)


def my_orders(request):
    orders = Order.objects.filter(user=request.user.pk, is_ordered= True).order_by('-created_at')

    context = {
        'orders': orders
    }
    return render(request, 'customers/my_orders.html', context)

def order_details(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_item = OrderedItem.objects.filter(order=order)
        subtotal = 0
        for item in ordered_item:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)


        context = {
            'order': order,
            'ordered_item': ordered_item,
            'subtotal': subtotal,
            'tax_data': tax_data
        }

    except:
        return redirect('customer')
    return render(request, 'customers/order_details.html', context)