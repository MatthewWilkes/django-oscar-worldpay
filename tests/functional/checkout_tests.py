# coding: utf-8
import sys
try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.importlib import import_module

from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_classes, get_model
from oscar.test.testcases import WebTestCase
from . import CheckoutMixin

GatewayForm = get_class('checkout.forms', 'GatewayForm')
CheckoutSessionData = get_class('checkout.utils', 'CheckoutSessionData')
RedirectRequired, UnableToTakePayment, PaymentError = get_classes(
    'payment.exceptions', [
        'RedirectRequired', 'UnableToTakePayment', 'PaymentError'])
UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')

Basket = get_model('basket', 'Basket')
Order = get_model('order', 'Order')
User = get_user_model()

# Python 3 compat
try:
    from imp import reload
except ImportError:
    pass


def reload_url_conf():
    # Reload URLs to pick up the overridden settings
    if settings.ROOT_URLCONF in sys.modules:
        reload(sys.modules[settings.ROOT_URLCONF])
    import_module(settings.ROOT_URLCONF)


class OrderTextMixin(object):
    is_anonymous = True

    def setUp(self):
        reload_url_conf()
        from worldpay import facade
        self.check_ip = facade.check_ip
        facade.check_ip = lambda request: True
        super(OrderTextMixin, self).setUp()
    
    def tearDown(self):
        from worldpay import facade
        facade.check_ip = self.check_ip
    
    def test_saves_guest_email_with_order(self):
        preview = self.ready_to_place_an_order(is_guest=True)
        worldpay = preview.forms['place_order_form'].submit()
        
        redirect = worldpay.location
        data = parse_qs(worldpay.location.split("?")[1])
        
        worldpay_agent = self.app_class(extra_environ=self.extra_environ)
        callback = worldpay_agent.post(reverse('worldpay-callback'), {
            'cartId':               data['cartId'][0],
            'amount':               data['amount'][0],
            'currency':             data['currency'][0],
            'transId':              '012345',
            'transStatus':          'Y',
            'M_user':               data['M_user'][0],
            'M_basket':             data['M_basket'][0],
            'M_authenticator':      data['M_authenticator'][0],
            'M_shipping_method':    data['M_shipping_method'][0],
            'M_shipping_address':   data['M_shipping_address'][0],
            'M_billing_address':    data['M_billing_address'][0],
            'M_order_kwargs':       data['M_order_kwargs'][0],
            'testMode':             '100',
        })
        
        order = Order.objects.all()[0]
        self.assertEqual('hello@egg.com', order.guest_email)
    

@override_settings(OSCAR_ALLOW_ANON_CHECKOUT=True)
class TestPlacingOrder(OrderTextMixin, WebTestCase, CheckoutMixin):
    pass

@override_settings(OSCAR_ALLOW_ANON_CHECKOUT=True)
class TestPlacingOrderWithForeignAddress(OrderTextMixin, WebTestCase, CheckoutMixin):
    
    def enter_shipping_address(self):
        self.create_shipping_country()
        address_page = self.get(reverse('checkout:shipping-address'))
        form = address_page.forms['new_shipping_address']
        form['first_name'] = u'マツ'
        form['last_name'] = u'ウリクス'
        form['line1'] = u'１０２　エリチュヴィネルツススツラス'
        form['line4'] = u'ベルィヌ'
        form['postcode'] = 'N12 9RT'
        form['phone_number'] = '01225 442244'
        form.submit()
        
    
