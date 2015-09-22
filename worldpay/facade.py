from __future__ import unicode_literals
import json

from django.conf import settings
from django.core.urlresolvers import reverse
from oscar.apps.payment.exceptions import PaymentError

from . import gateway


def build_payment_url(total, order_number, user, basket, shipping_method, shipping_address, billing_address, M_params=None, test_mode=False):
    cart_id = "{0}".format(order_number).encode("ascii")
    if total is None:
        total = basket.total_incl_tax.to_eng_string().encode('ascii')
    else:
        total = total.incl_tax.to_eng_string().encode('ascii')
    currency = basket.currency.encode("ascii")
    try:
        user_id = user.pk
    except AttributeError:
        user_id = None
    basket_id = basket.pk
    instance_id = "{0}".format(settings.WORLDPAY_INSTANCE_ID).encode("ascii")
    if M_params is None:
        M_params = {}
    shipping_address.save()
    if billing_address is not None:
        billing_address.save()
        address = billing_address
    else:
        address = shipping_address
    
    M_params.update({
        b'user': "{0}".format(user_id).encode("ascii"),
        b'basket': "{0}".format(basket_id).encode("ascii"),
        b'shipping_method': "{0}".format(shipping_method.code).encode("ascii"),
        b'shipping_address': "{0}".format(shipping_address.pk).encode("ascii"),
        b'billing_address': "{0}".format(getattr(billing_address, 'pk', None)).encode("ascii"),
    })
    
    worldpay_params = {
        b'fixContact': 'True',
        b'hideContact': 'False',
        
        b'name':     address.name,
        b'address1': address.line1,
        b'address2': address.line2,
        b'address3': address.line3,
        b'town':     address.city,
        b'region':   address.state,
        b'postcode': address.postcode,
        b'tel':      address.phone_number.as_international or '',
        b'country':  address.country.code
    }
    try:
        worldpay_params[b'email'] = user.email
    except AttributeError:
        worldpay_params[b'email'] = json.loads(M_params[b'order_kwargs'].decode("utf-8"))["guest_email"]
    
    
    return gateway.build_payment_url(instance_id, cart_id, total, currency, worldpay_params=worldpay_params, M_params=M_params, secret=settings.SECRET_KEY.encode("utf-8"), SignatureFields=[field.encode("ascii") for field in settings.WORLDPAY_SIGNATURE_FIELDS], MD5Secret=settings.WORLDPAY_MD5_SECRET.encode("utf-8"), test_mode=test_mode)

def confirm(request):
    if not check_ip(request):
        raise PaymentError("Error tracing origin point of callback")
    try:
        return gateway.confirm(request, settings.SECRET_KEY.encode("utf-8"))
    except ValueError as e:
        raise PaymentError(str(e))

def check_ip(request):
    """Check if an IP address has a reverse DNS that matches worldpay.com, and if
    it does, check that that hostname has the IP as one of its resolvables."""
    try:
        header = settings.WORLDPAY_REMOTE_ADDRESS_HEADER
    except AttributeError:
        header = 'REMOTE_ADDR'
    # Handle X-Forwarded-For
    ip = request.META[header].split(',')[0]
    return gateway.check_ip(ip)
