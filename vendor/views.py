from django.shortcuts import render, get_object_or_404, redirect
from .forms import VendorForm
from accounts.forms import UserProfileForm
from .models import Vendor
from accounts.models import UserProfile
from django.contrib import messages
# Create your views here.


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
