from django.conf import settings
from django.core.urlresolvers import reverse
from oscar.apps.payment.exceptions import PaymentError

from . import gateway


def build_payment_url(order_number, user, basket, shipping_method, shipping_address, billing_address, M_params=None, test_mode=False):
    cart_id = order_number
    total = basket.total_incl_tax
    currency = basket.currency
    try:
        user_id = user.pk
    except AttributeError:
        user_id = None
    basket_id = basket.pk
    instance_id = settings.WORLDPAY_INSTANCE_ID
    if M_params is None:
        M_params = {}
    shipping_address.save()
    if billing_address is not None:
        billing_address.save()
    M_params.update({
        'user': user_id,
        'basket': basket_id,
        'shipping_method': shipping_method.code,
        'shipping_address': shipping_address.pk,
        'billing_address': getattr(billing_address, 'pk', None),
    })
    return gateway.build_payment_url(instance_id, cart_id, total, currency, M_params=M_params, secret=settings.SECRET_KEY, test_mode=test_mode)

def confirm(request):
    if not check_ip(request):
        raise PaymentError("Nope.")
    return gateway.confirm(request)

def check_ip(request):
    """Check if an IP address has a reverse DNS that matches worldpay.com, and if
    it does, check that that hostname has the IP as one of its resolvables."""
    try:
        header = settings.WORLDPAY_REMOTE_ADDRESS_HEADER
    except AttributeError:
        header = 'REMOTE_ADDR'
    ip = request.META[header]
    return gateway.check_ip(ip)
