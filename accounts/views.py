from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages
from vendor.forms import VendorForm
from django.contrib import auth
from .utils import detectUser
from django.contrib.auth.decorators import login_required

# Create your views here.

def registerUser(request):

    if request.user.is_authenticated:
        messages.warning(request, "You are already Logged In")
        return redirect("dashboard")
    

    elif request.method == "POST":
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

    if request.user.is_authenticated:
        messages.warning(request, "You are already Logged In")
        return redirect("dashboard")
    
    elif request.method == "POST":
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
    

def login(request):

    if request.user.is_authenticated:
        messages.warning(request, "You are already Logged In")
        return redirect("myAccount")
    
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email= email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success( request, 'You are logged in')
            return redirect('myAccount')


        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info( request, 'You are logged out')
    return redirect('login')


@login_required(login_url="login")
def myAccount(request):
    user =  request.user
    redirecturl = detectUser(user)
    return redirect(redirecturl)

@login_required(login_url="login")
def customerDashboard(request):
    return render(request, "accounts/customerDashboard.html")


@login_required(login_url="login")
def vendorDashboard(request):
    return render(request, "accounts/vendorDashboard.html")