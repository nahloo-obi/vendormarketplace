import datetime

def generate_order_number(pk):
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = now + str(pk)

    return order_number

