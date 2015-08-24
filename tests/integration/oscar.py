from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from oscar.test.factories import create_product
from oscar.test.factories import create_order
from oscar.test.factories import create_basket
from oscar.test.factories import UserFactory
import pytz


class TestURLsFromOrder(TestCase):

    def setUp(self):
        from django.conf import settings
        self.secret = settings.KALYX_DOWNLOAD_SECRET
        self.user = UserFactory()
        self.products = [create_product(partner_sku=314, partner_name='kalyx', price=Decimal('2.17')),
                         create_product(partner_sku=988, partner_name='kalyx', price=Decimal('3.12'))]
        
        basket = create_basket(empty=True)
        basket.add_product(self.products[0])
        basket.add_product(self.products[0])
        basket.add_product(self.products[1])
        basket.add_product(self.products[1])
        self.order = create_order(number='10001', basket=basket, user=self.user, date_placed=datetime(2015, 1, 2, 3, 13, 45, 0, pytz.UTC).isoformat())
    
        from worldpay.facade import build_payment_url
        self.build_payment_url = build_payment_url
    
    def test_simple_payment_url_is_as_expected(self):
        url = self.build_payment_url(self.order.number, unicode(self.order.price_incl_tax), self.order.price_incl_tax.currency)
        self.assertNotIn('testMode', url)
        self.assertEqual(url, 'https://secure.worldpay.com/wcc/purchase?currency=GBP&instId=12345&amount=12.00&desc=&cartId=6789')

    def test_test_mode_is_opt_in(self):
        url = self.build_payment_url(self.order.number, unicode(self.order.price_incl_tax), self.order.price_incl_tax.currency, test_mode=True)
        self.assertIn('testMode', url)
        self.assertEqual(url, 'https://secure-test.worldpay.com/wcc/purchase?cartId=6789&instId=12345&currency=GBP&amount=12.00&testMode=100&desc=')
    
