from .models import Cart
from menu.models import Item


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user.pk)
            if cart_items:
                for cartitem in cart_items:
                    cart_count += cartitem.quantity
            else:
                cart_count = 0

        except:
            cart_count = 0

    return dict(cart_count=cart_count)


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    sum_total = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user.pk)

        for item in cart_items:
            storeItem = Item.objects.get(pk=item.item.id)
            subtotal += (storeItem.price * item.quantity)

        sum_total = subtotal + tax
        
    return dict(subtotal=subtotal, tax=tax, sum_total=sum_total)