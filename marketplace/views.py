from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from vendor.models import Vendor
from menu.models import Category, Item
from django.db.models import Prefetch

from .context_processors import get_cart_counter, get_cart_amount
from .models import Cart
from vendor.models import OpeningHours

from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from datetime import date
# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active = True)
    vendor_count = vendors.count()
    context ={
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug= vendor_slug)

    categories = Category.objects.filter(vendor= vendor.pk).prefetch_related(
        Prefetch(
        'items',
        queryset = Item.objects.filter(is_available = True)
        )
        
    ) 

    opening_hours = OpeningHours.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    #Check current day opening hour
    get_today = date.today()
    today = get_today.isoweekday()    #to get the week day number
    
    current_day_opening_hour = OpeningHours.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user.pk)
    else:
        cart_items = None


    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items' : cart_items,
        'opening_hours': opening_hours,
        'current_day_opening_hour': current_day_opening_hour
    }

    return render(request, 'marketplace/vendor_detail.html', context)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def add_to_cart(request, item_id=None):
    if request.user.is_authenticated:

        if is_ajax(request=request):
            try:
                storeitem = Item.objects.get(id=item_id)
                try:
                    
                    check_cart_item = Cart.objects.filter(user=request.user, item=storeitem)
                    if check_cart_item.exists():
                        check_cart = check_cart_item[0]
                        print("updating cart quantity")
                        check_cart.quantity += 1
                        check_cart.save()
                        return JsonResponse({
                        'status': 'success',
                        'message': 'Item increased',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                        'cart_amount': get_cart_amount(request),

                        })

                    else:

                        create_cart = Cart.objects.create(user=request.user, item=storeitem, quantity=1)

                        return JsonResponse({
                        'status': 'success',
                        'message': 'Item added to cart',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                        'cart_amount': get_cart_amount(request),
                        })
                    
                except:
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'Item does not existed'
                        })

            except:
                return JsonResponse({
                'status': 'Failed',
                'message': 'Product does not exist'
                })
        else:
            return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid request'
        })
    
    else:

        return JsonResponse({
            'status': 'login_required',
            'message': 'Please Login to add to cart'
        })
    
def decrease_cart(request, item_id):
    if request.user.is_authenticated:
        if is_ajax(request=request):
            try:
                storeitem = Item.objects.get(id=item_id)
                try:
                    
                    check_cart_item = Cart.objects.filter(user=request.user, item=storeitem)
                    if check_cart_item.exists():
                        check_cart = check_cart_item[0]
                        if check_cart.quantity > 1:
                            check_cart.quantity -= 1
                            check_cart.save()
                        else:
                            check_cart.delete()
                            check_cart.quantity = 0

                        return JsonResponse({
                        'status': 'success',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                        'cart_amount': get_cart_amount(request),

                        })

                    
                except:
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'Item does not existed'
                        })

            except:
                return JsonResponse({
                'status': 'Failed',
                'message': 'Product does not exist'
                })
        else:
            return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid request'
        })
    
    else:

        return JsonResponse({
            'status': 'login_required',
            'message': 'Please Login to add to cart'
        })

@login_required(login_url="login")
def cart(request):
    cart_items = Cart.objects.filter(user=request.user.pk).order_by('created_at')
    
    context = {
        'cartItems': cart_items
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:

        if is_ajax(request=request):
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'success', 'message': 'Item removed from cart!', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amount(request),})
                
            except:
                 return JsonResponse({
                'status': 'Failed',
                'message': 'Cart item does not exist!'
                })
        else:
            return JsonResponse({})
        

def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:

        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        #get vendors by item
        fetch_vendor_by_store_item = Item.objects.filter(item_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)

        vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_store_item) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))

        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))  # using string representation technique

            vendors = Vendor.objects.filter(
                Q(id__in=fetch_vendor_by_store_item) | Q(vendor_name__icontains=keyword, 
                    is_approved=True, user__is_active=True, 
                    user_profile__location__distance_lte=(pnt, D(km=radius)))
                        ).annotate(distance=Distance("user_profile__location", pnt)
                                ).order_by('distance')
            
            for v in vendors:
                v.kms = round(v.distance.km, 1)

        vendor_count = vendors.count()

        context ={
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address,
        }

        return render(request, 'marketplace/listings.html', context)