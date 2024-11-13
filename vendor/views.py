from django.shortcuts import render, get_object_or_404, redirect
from .forms import VendorForm
from accounts.forms import UserProfileForm
from .models import Vendor
from accounts.models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_vendor_role
from menu.models import Category, Item
from menu.forms import CategoryForm, ItemForm
from django.template.defaultfilters import slugify
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

@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category added successfully')
            return redirect('menu_builder') 

        else:
            print(form.errors)


    form = CategoryForm()
    context = {
        'form': form
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('menu_builder') 

        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category' : category
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category Deleted Successfully")
    return redirect('menu_builder')

@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)

        if form.is_valid():
            item_title = form.cleaned_data['item_title']
            item = form.save(commit=False)
            item.vendor = get_vendor(request)
            item.slug = slugify(item_title)
            form.save()
            messages.success(request, 'Store item updated successfully')
            return redirect('items_by_category', item.category.id) 

        else:
            print(form.errors)
    else:
        form = ItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form
    }


    return render(request, 'vendor/add_item.html', context)


def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            item_title = form.cleaned_data['item_title']
            item = form.save(commit=False)
            item.vendor = get_vendor(request)
            item.slug = slugify(item_title)
            form.save()
            messages.success(request, 'Item updated successfully')
            return redirect('items_by_category', item.category.id)

        else:
            print(form.errors)
    else:
        form = ItemForm(instance=item)

    context = {
        'form': form,
        'item' : item
    }
    return render(request, 'vendor/edit_item.html', context)


@login_required(login_url="login")
@user_passes_test(check_vendor_role)
def delete_item(request, pk=None):
    item = get_object_or_404(Item, pk=pk)
    item.delete()
    messages.success(request, "Item Deleted Successfully")
    return redirect('items_by_category', item.category.id)
