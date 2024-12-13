from .models import Cart
from menu.models import Item
from .models import Tax


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
    tax_dict = {}

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user.pk)

        for item in cart_items:
            storeItem = Item.objects.get(pk=item.item.id)
            subtotal += (storeItem.price * item.quantity)

        Get_tax = Tax.objects.filter(is_active=True)

        for i in Get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/ 100, 2)
            tax_dict.update({tax_type:{str(tax_percentage):tax_amount}})

       

        # for key in tax_dict.values():
        #     for x in key.values():
        #         tax = tax + x
        
        tax = sum(x for key in tax_dict.values() for x in key.values())

        sum_total = subtotal + tax
        
    return dict(subtotal=subtotal, tax=tax, sum_total=sum_total, tax_dict=tax_dict)