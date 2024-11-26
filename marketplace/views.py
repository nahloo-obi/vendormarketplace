from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from vendor.models import Vendor
from menu.models import Category, Item
from django.db.models import Prefetch

from .context_processors import get_cart_counter
from .models import Cart

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
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user.pk)
    else:
        cart_items = None


    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items' : cart_items
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
                        'qty': check_cart.quantity

                        })

                    else:

                        create_cart = Cart.objects.create(user=request.user, item=storeitem, quantity=1)

                        return JsonResponse({
                        'status': 'success',
                        'message': 'Item added to cart',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity
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
            print("error")
            return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid request'
        })
    
    else:

        return JsonResponse({
            'status': 'Failed',
            'message': 'Please Login to add to cart'
        })
