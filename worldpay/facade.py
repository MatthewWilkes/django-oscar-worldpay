from gateway import build_payment_url

def build_payment_url(order, total, currency, test_mode=False):
    cart_id = order.number
    instance_id = settings.WORLDPAY_INSTANCE_ID
    return build_payment_url(instance_id, cart_id, total, currency, test_mode=test_mode)
