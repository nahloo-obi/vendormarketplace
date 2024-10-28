from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages
from vendor.forms import VendorForm

# Create your views here.

def registerUser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)  #hashpassword
            user.role = User.CUSTOMER
            form.save()
        
        else:
            print(form.errors)

        messages.success(request, "Account Registeration Successful")
        return redirect('registerUser')
    
    else:

        form = UserForm()
        context = {
            'form': form,
        }
        return render(request, 'accounts/registerUser.html', context)
    

def registerVendor(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                first_name= first_name,
                last_name = last_name,
                username = username,
                email = email,
                password = password
            )
            user.role = User.VENDOR
            user.save()

            vendor = vendor_form.save(commit=False)

            vendor.user = user

            user_profile = UserProfile.objects.get(user=user)
 
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, "Business registered successfully, awaiting aproval from admin")
            return redirect('registerVendor')

        else:
            print(form.errors)
    else:

        form = UserForm()
        vendor_form = VendorForm()

        context = {
            "form" : form,
            "vendor_form": vendor_form
        }
        return render(request, 'accounts/registerVendor.html', context)