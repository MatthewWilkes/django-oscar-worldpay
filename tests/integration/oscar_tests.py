from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal
import unittest

from django.test import TestCase
from django.test.client import RequestFactory
from oscar.apps.payment.exceptions import PaymentError
from oscar.test.factories import create_product
from oscar.test.factories import create_order
from oscar.test.factories import create_basket
from oscar.test.factories import UserFactory
import pytz


class TestUrlsFromOrder(TestCase):

    def setUp(self):
        from django.conf import settings
        self.user = UserFactory()
        self.products = [create_product(price=Decimal('2.17')),
                         create_product(price=Decimal('3.12'))]
        
        basket = create_basket(empty=True)
        basket.add_product(self.products[0])
        basket.add_product(self.products[0])
        basket.add_product(self.products[1])
        basket.add_product(self.products[1])
        self.order = create_order(number='10001', basket=basket, user=self.user, date_placed=datetime(2015, 1, 2, 3, 13, 45, 0, pytz.UTC).isoformat())
    
        from worldpay.facade import build_payment_url
        self.build_payment_url = build_payment_url
    
    def test_simple_payment_url_is_as_expected(self):
        url = self.build_payment_url(self.order.number, unicode(self.order.basket_total_incl_tax), self.order.currency)
        self.assertNotIn('testMode', url)
        self.assertEqual(url, 'https://secure.worldpay.com/wcc/purchase?instId=12345&cartId=10001&currency=GBP&amount=10.58&desc=')

    def test_test_mode_is_opt_in(self):
        url = self.build_payment_url(self.order.number, unicode(self.order.basket_total_incl_tax), self.order.currency, test_mode=True)
        self.assertIn('testMode', url)
        self.assertEqual(url, 'https://secure-test.worldpay.com/wcc/purchase?instId=12345&cartId=10001&currency=GBP&amount=10.58&desc=&testMode=100')
    

class TestConfirmOrder(TestCase):

    def setUp(self):
        from worldpay import facade
        self.confirm = facade.confirm
        self.check_ip = facade.check_ip
        facade.check_ip = lambda request: request.META['REMOTE_ADDR'].startswith("127.")
    
    def tearDown(self):
        from worldpay import facade
        facade.check_ip = self.check_ip
    
    def test_POST_from_8_8_8_8_is_rejected(self):
        data = {
            'cartId':       '10001',
            'cost':         '12.50',
            'currency':     'GBP',
            'testMode':     0,
            'transStatus':  'Y',
        }
        
        post_request = RequestFactory().post('/callback/1', data, REMOTE_ADDR='8.8.8.8')
        with self.assertRaises(PaymentError):
            self.confirm(post_request)
        
    def test_POST_from_127_0_0_2_is_rejected(self):
        """ We've faked the IP checking to only accept posts from localhost. This should work."""
        data = {
            'cartId':       '10001',
            'cost':         '12.50',
            'currency':     'GBP',
            'testMode':     0,
            'transStatus':  'Y',
        }
        
        post_request = RequestFactory().post('/callback/1', data, REMOTE_ADDR='127.0.0.2')
        self.confirm(post_request)
        

class TestValidateIp(TestCase):

    def setUp(self):
        from worldpay import facade
        self.check_ip = facade.check_ip
    
    def test_8_8_8_8_is_rejected(self):
        post_request = RequestFactory().post('/callback/1', {}, REMOTE_ADDR='8.8.8.8')
        self.assertFalse(self.check_ip(post_request))
        
    def test_mm2imssq1p_outbound_wp3_rbsworldpay_com_is_allowed(self):
        """ This appears to be a real hostname that worldpay uses... """
        import socket
        ip = socket.gethostbyname('mm2imssq1p.outbound.wp3.rbsworldpay.com')
        post_request = RequestFactory().post('/callback/1', {}, REMOTE_ADDR=ip)
        self.assertTrue(self.check_ip(post_request))
    
    def test_incorrect_ipv6_is_rejected(self):
        """ Tests that an IPv6 request from example.com is rejected"""
        post_request = RequestFactory().post('/callback/1', {}, REMOTE_ADDR='2606:2800:220:1:248:1893:25c8:1946')
        self.assertFalse(self.check_ip(post_request))
    
    @unittest.skip
    def test_correct_ipv6_is_allowed(self):
        """ Tests that an IPv6 request from worldpay.com is allowed"""
        # We don't have an IPv6 address for them...
        post_request = RequestFactory().post('/callback/1', {}, REMOTE_ADDR='::1')
        self.assertTrue(self.check_ip(post_request))
    