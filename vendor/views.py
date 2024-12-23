from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm
from .models import Vendor, OpeningHours
from accounts.models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_vendor_role
from menu.models import Category, Item
from menu.forms import CategoryForm, ItemForm
from django.template.defaultfilters import slugify
from marketplace.views import is_ajax
from orders.models import Order, OrderedItem

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
            category.save()
            category.slug = slugify(category_name) + '-' + str(category.id)
            category.save()

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
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

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


def opening_hours(request):
    opening_hours = OpeningHours.objects.filter(vendor=get_vendor(request).pk)
    form = OpeningHourForm()

    context = {
        'form': form,
        'opening_hours' : opening_hours
    }

    return render(request, 'vendor/opening_hours.html', context)


def add_opening_hours(request):
    if request.user.is_authenticated:
        if is_ajax(request=request) and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')

            try:
                hour = OpeningHours.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHours.objects.get(id=hour.id)
                    
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}

                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
               
                return JsonResponse(response)
            
            except IntegrityError as e:
                response = {
                    'status': 'failed',
                    'message': from_hour + '-' + to_hour + ' already exists for this day!'
                }
                return JsonResponse(response)
                
        else:
            return HttpResponse('Invalid request')
        

def remove_opening_hours(request, pk):
    if request.user.is_authenticated:
        if is_ajax(request=request):
            hour = get_object_or_404(OpeningHours, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})


def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_item = OrderedItem.objects.filter(order=order, storeitem__vendor = get_vendor(request))

        context = {
            'order': order,
            'ordered_item': ordered_item,
            'subtotal': order.get_total_by_vendor()['subtotal'],
            'tax_dict': order.get_total_by_vendor()['tax_data'],
            'subtotal' : order.get_total_by_vendor()['grand_total'],
        }

    except:
        return redirect('vendor')
    
    return render(request, 'vendor/order_detail.html', context)



def my_orders(request):
    vendor = Vendor.objects.get(user = request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    

    context = {
        'orders': orders,
    }

    return render(request, 'vendor/my_orders.html', context)