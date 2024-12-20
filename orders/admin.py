from django.contrib import admin
from .models import Payment, Order, OrderedItem
# Register your models here.

class OrderedItemInline(admin.TabularInline):
    model = OrderedItem
    readonly_fields = ('order', 'payment', 'user', 'storeitem', 'quantity', 'price', 'amount')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'order_placed_to','is_ordered']
    inlines = [OrderedItemInline]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedItem)

