import datetime
import json

def generate_order_number(pk):
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = now + str(pk)

    return order_number



def order_total_by_vendor(order, vendor_id):
    

    subtotal = 0
    tax = 0
    tax_dict = {}
    
    if order.total_data:
        total_data = json.loads(order.total_data)
        data = total_data.get(str(vendor_id))


        for key, value in data.items():
            subtotal += float(key)
            value = value.replace("'", '"')
            value  = json.loads
            tax_dict.update(value)

            for i in value:
                for j in value[i]:
                    tax += float(value[i][j])

    grand_total = float(subtotal) + float(tax)

    context = {
        'subtotal': subtotal,
        'tax_data': tax_dict,
        'grand_total': grand_total
    }

    return context