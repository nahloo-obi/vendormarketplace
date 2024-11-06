from django.shortcuts import render, get_object_or_404, redirect
from .forms import VendorForm
from accounts.forms import UserProfileForm
from .models import Vendor
from accounts.models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_vendor_role
from menu.models import Category, Item
# Create your views here.


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user.pk)

    return vendor

@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def vendor_profile(request):
    profile = get_object_or_404(UserProfile, user = request.user.pk)
    vendor = get_object_or_404(Vendor, user = request.user.pk)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)


        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Profile Updated")
            return redirect('vendorprofile')
        
        else:
            return redirect('vendorprofile')

    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)
    context = {
        'profile_form' : profile_form,
        'vendor_form' : vendor_form,
        'profile': profile,
        'vendor': vendor
        
    }

    return render(request, 'vendor/vendorprofile.html', context)

@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor)

    context = {
        'categories': categories
    }
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def items_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)

    items = Item.objects.filter(vendor=vendor, category=category)
    context = {
        'items': items,
        'category': category
    }
    return render(request, 'vendor/items_by_category.html', context)

def add_category(request):
    return render(request, 'vendor/add_category.html')
