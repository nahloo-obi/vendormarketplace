from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages

# Create your views here.


@login_required(login_url='login')
def customer_profile(request):
    print('customer profile')
    profile = get_object_or_404(UserProfile, user = request.user.pk)

    if request.method == "POST":
        print('post')
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            print('no error')
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile Updated')
            return redirect('customer_profile')
        else:
            print('error')
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