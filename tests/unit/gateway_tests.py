from __future__ import unicode_literals
from django.test import TestCase

from worldpay.gateway import build_payment_url


class TestUrlGeneration(TestCase):

    def test_simple_payment_url_is_as_expected(self):
        url = build_payment_url(b'12345', b'6789', b'12.00', b'GBP')
        self.assertNotIn('testMode', url)
        self.assertEqual('https://secure.worldpay.com/wcc/purchase?instId=12345&cartId=6789&currency=GBP&amount=12.00&desc=', url)

    def test_test_mode_is_opt_in(self):
        url = build_payment_url(b'12345', b'6789', b'12.00', b'GBP', test_mode=True)
        self.assertIn('testMode', url)
        self.assertEqual('https://secure-test.worldpay.com/wcc/purchase?instId=12345&cartId=6789&currency=GBP&amount=12.00&desc=&testMode=100', url)
    
    def test_additional_parameters_are_passed_and_protected(self):
        url = build_payment_url(b'12345', b'6789', b'12.00', b'GBP', M_params={b'one': b'two'}, secret=b"gobbledegook", test_mode=True)
        self.assertIn('testMode', url)
        self.assertEqual('https://secure-test.worldpay.com/wcc/purchase?instId=12345&cartId=6789&currency=GBP&amount=12.00&desc=&M_one=two&M_authenticator=9af607fbc8aa172cd2ff6ed1bbc91c7724edcc22a87836b55f1bb940778d6211&testMode=100', url)
    
