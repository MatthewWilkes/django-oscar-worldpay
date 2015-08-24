from __future__ import unicode_literals

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


def build_payment_url(instance_id, cart_id, total, currency, test_mode=False):
    data = {
        'instId':           instance_id,
        'cartId':           cart_id,
        'currency':         currency,
        'amount':           total,
        'desc':             '',
    }
    if test_mode:
        data['testMode'] = '100'
        base = "https://secure-test.worldpay.com/wcc/purchase?"
    else:
        base = "https://secure.worldpay.com/wcc/purchase?"
    
    return base + urlencode(data)