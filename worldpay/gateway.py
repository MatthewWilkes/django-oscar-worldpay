from __future__ import unicode_literals

def build_payment_url(instance_id, card_id, total, currency, test_mode=False):
    data = {
        'instId':           instance_id,
        'cartId':           cart_id,
        'currency':         currency,
        'amount':           total,
        'desc':             '',
        'M_recipient':      'tiq@uk.worldpay.com',
        'M_subject':        'WorldPay example',
        'MC_callback':      {{ worldpay_callback }},
    }
    if test_mode:
        data['testMode'] = '100'
    
    
    pass