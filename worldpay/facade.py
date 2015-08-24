from django.conf import settings

import gateway


def build_payment_url(order_number, total, currency, test_mode=False):
    cart_id = order_number
    instance_id = settings.WORLDPAY_INSTANCE_ID
    return gateway.build_payment_url(instance_id, cart_id, total, currency, test_mode=test_mode)
