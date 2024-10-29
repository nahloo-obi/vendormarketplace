from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages
from vendor.forms import VendorForm
from django.contrib import auth
from .utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from .utils import send_email_verification
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


# restrict user switch
def check_vendor_role(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied
    
def check_customer_role(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



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
            
             # send email verification to new user

            mail_subject = 'Email Verification'
            email_template = 'accounts/emails/account_verification_email.html'

            send_email_verification(request, user, mail_subject, email_template)
            messages.success(request, "Account Registeration Successful")
        
        else:
            print(form.errors)

        
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

            # send email verification to new vendor
            mail_subject = 'Email Verification'
            email_template = 'accounts/emails/account_verification_email.html'

            send_email_verification(request, user, mail_subject, email_template)

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
    


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully")
        return redirect('myAccount')
    else:
        messages.error(request, "Activation link invalid")
        return redirect('myAccount')

    

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
@user_passes_test(check_customer_role)
def customerDashboard(request):
    return render(request, "accounts/customerDashboard.html")


@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def vendorDashboard(request):
    return render(request, "accounts/vendorDashboard.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)


            mail_subject = 'Password Reset'
            email_template = 'accounts/emails/reset_password_email.html'

            send_email_verification(request, user, mail_subject, email_template)
            messages.success(request, "Password reset link has been sent to your email address")

            return redirect('login')
        else:
           messages.error(request, "Account does not exist")
           return redirect('login')
         
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request, "Expired Link")
        return redirect('myAccount')
     

def reset_password(request):
    if request.method == "POST":
        password  = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect('login')
        else:
            messages.error(request, "Password do not match!")
            return redirect('reset_password')

    return render(request, 'accounts/reset_password.html')