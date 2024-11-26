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