from django.conf import settings
from oscar.apps.payment.exceptions import PaymentError

from . import gateway


def build_payment_url(order_number, total, currency, test_mode=False):
    cart_id = order_number
    instance_id = settings.WORLDPAY_INSTANCE_ID
    return gateway.build_payment_url(instance_id, cart_id, total, currency, test_mode=test_mode)

def confirm(request):
    if not check_ip(request):
        raise PaymentError("Nope.")

def check_ip(request):
    """Check if an IP address has a reverse DNS that matches worldpay.com, and if
    it does, check that that hostname has the IP as one of its resolvables."""
    try:
        header = settings.WORLDPAY_REMOTE_ADDRESS_HEADER
    except AttributeError:
        header = 'REMOTE_ADDR'
    ip = request.META[header]
    return gateway.check_ip(ip)
