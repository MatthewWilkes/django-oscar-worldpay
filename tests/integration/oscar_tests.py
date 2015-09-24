from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal
import unittest

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from oscar.apps.payment.exceptions import PaymentError
from oscar.apps.shipping import methods as shipping_methods
from oscar.test.factories import create_product
from oscar.test.factories import create_order
from oscar.test.factories import create_basket
from oscar.apps.address import models as address_models
from oscar.apps.order import models as order_models
import pytz
from six import text_type


class TestUrlsFromOrder(TestCase):
    
    maxDiff = 2500
    
    def setUp(self):
        from django.conf import settings
        self.products = [create_product(price=Decimal('2.17')),
                         create_product(price=Decimal('3.12'))]
        
        self.basket = create_basket(empty=True)
        self.basket.add_product(self.products[0])
        self.basket.add_product(self.products[0])
        self.basket.add_product(self.products[1])
        self.basket.add_product(self.products[1])
        user = User.objects.create_user(username='test', password='pass', email='test@example.com')
        self.order = create_order(number='10001', user=user, basket=self.basket)
        country = address_models.Country.objects.create(iso_3166_1_a2='GB', name="Great Britain")
        self.address = order_models.ShippingAddress(
            first_name='', last_name='Barrington', line1="75 Smith Road",
            postcode="N4 8TY", country=country, phone_number='01225 442244')
    
        from worldpay.facade import build_payment_url
        self.build_payment_url = build_payment_url
    
    def test_simple_payment_url_is_as_expected(self):
        url = self.build_payment_url(None, self.order.number, self.order.user, self.basket, shipping_methods.Free(), self.address, None)
        self.assertNotIn('testMode', url)
        self.assertEqual('https://secure.worldpay.com/wcc/purchase?instId=12345&cartId=10001&currency=GBP&amount=10.58&desc=&M_basket=1&M_billing_address=None&M_shipping_address=1&M_shipping_method=free-shipping&M_user=1&M_authenticator=77cfb68a1b094c753709ec5ab0be6b37133aaa998d31f40139c1229f21f6468f&address1=75+Smith+Road&address2=&address3=&country=GB&email=test%40example.com&fixContact=True&hideContact=False&name=Barrington&postcode=N4+8TY&region=&tel=01225+442244&town=&signature=ffbf1d6b60214aa1799e4015d5376562', url)

    def test_test_mode_is_opt_in(self):
        url = self.build_payment_url(None, self.order.number, self.order.user, self.basket, shipping_methods.Free(), self.address, None, test_mode=True)
        self.assertIn('testMode', url)
        self.assertEqual('https://secure-test.worldpay.com/wcc/purchase?instId=12345&cartId=10001&currency=GBP&amount=10.58&desc=&M_basket=1&M_billing_address=None&M_shipping_address=1&M_shipping_method=free-shipping&M_user=1&M_authenticator=77cfb68a1b094c753709ec5ab0be6b37133aaa998d31f40139c1229f21f6468f&address1=75+Smith+Road&address2=&address3=&country=GB&email=test%40example.com&fixContact=True&hideContact=False&name=Barrington&postcode=N4+8TY&region=&tel=01225+442244&town=&signature=ffbf1d6b60214aa1799e4015d5376562&testMode=100', url)
    

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
            'instId':       '100',
            'cartId':       '10001',
            'amount':       '12.50',
            'currency':     'GBP',
            'testMode':     '0',
            'transStatus':  'Y',
            'M_authenticator': 'f2b4597421c94db367d412c8af2be71631b1c90323cbae297511ec33c0f16e06',
        }
        
        post_request = RequestFactory().post('/callback/1', data, REMOTE_ADDR='8.8.8.8')
        with self.assertRaises(PaymentError):
            self.confirm(post_request)
        
    def test_POST_from_127_0_0_2_is_allowed(self):
        """ We've faked the IP checking to only accept posts from localhost. POSTing from there will not raise an error."""
        data = {
            'instId':       '100',
            'cartId':       '10001',
            'amount':       '12.50',
            'currency':     'GBP',
            'testMode':     '0',
            'transStatus':  'Y',
            'M_authenticator': 'f2b4597421c94db367d412c8af2be71631b1c90323cbae297511ec33c0f16e06',
        }
        
        post_request = RequestFactory().post('/callback/1', data, REMOTE_ADDR='127.0.0.2')
        self.confirm(post_request)
    
    def test_successful_post_contains_relevant_data(self):
        """ A successful confirmation should return information to finalise the order with. """
        data = {
            'instId':       '100',
            'cartId':       '10001',
            'amount':       '12.50',
            'currency':     'GBP',
            'testMode':     '0',
            'transStatus':  'Y',
            'M_authenticator': 'f2b4597421c94db367d412c8af2be71631b1c90323cbae297511ec33c0f16e06',
        }
        
        post_request = RequestFactory().post('/callback/1', data, REMOTE_ADDR='127.0.0.2')
        result = self.confirm(post_request)
        self.assertEqual(result['amount'], '12.50')
        self.assertEqual(result['cartId'], '10001')
        

    def test_M_data_is_passed_through_with_valid_checksum(self):
        """ A successful confirmation should return the M_data fields we passed in. """
        data = {
            'instId':       '100',
            'cartId':       '10001',
            'amount':       '12.50',
            'currency':     'GBP',
            'testMode':     '0',
            'transStatus':  'Y',
            'M_foo':        'bar',
            'M_authenticator': '1ebd751273b8748cdaa0b073c30afcd8e959ee7db0600faa1387814d0aa8cc3b',
        }
        
        post_request = RequestFactory().post('/callback/1', data, REMOTE_ADDR='127.0.0.2')
        result = self.confirm(post_request)
        self.assertEqual(result['M_foo'], 'bar')

    def test_failure_occurs_with_invalid_checksum(self):
        """ If we don't provide a valid checksum the request fails """
        data = {
            'instId':       '100',
            'cartId':       '10001',
            'amount':       '12.50',
            'currency':     'GBP',
            'testMode':     '0',
            'transStatus':  'Y',
            'M_authenticator': 'FFFF'
        }
        
        post_request = RequestFactory().post('/callback/1', data, REMOTE_ADDR='127.0.0.2')
        with self.assertRaises(PaymentError):
            result = self.confirm(post_request)
        
    def test_failure_occurs_with_failed_status(self):
        """ If the transaction wasn't authorised the request fails """
        data = {
            'instId':       '100',
            'cartId':       '10001',
            'amount':       '12.50',
            'currency':     'GBP',
            'testMode':     '0',
            'transStatus':  'F',
            'M_authenticator': 'f2b4597421c94db367d412c8af2be71631b1c90323cbae297511ec33c0f16e06',
        }
        
        post_request = RequestFactory().post('/callback/1', data, REMOTE_ADDR='127.0.0.2')
        with self.assertRaises(PaymentError):
            result = self.confirm(post_request)
        
    
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
    
