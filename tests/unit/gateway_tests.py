from __future__ import unicode_literals
from django.test import TestCase

class TestURLs(TestCase):

    def setUp(self):
        from worldpay.gateway import build_payment_url
        self.build_payment_url = build_payment_url
    
    def test_simple_payment_url_is_as_expected(self):
        url = self.build_payment_url('12345', '6789', '12.00', 'GBP')
        self.assertNotIn('testMode', url)
        self.assertEqual(url, 'https://secure.worldpay.com/wcc/purchase?currency=GBP&instId=12345&amount=12.00&desc=&cartId=6789')

    def test_test_mode_is_opt_in(self):
        url = self.build_payment_url('12345', '6789', '12.00', 'GBP', True)
        self.assertIn('testMode', url)
        self.assertEqual(url, 'https://secure-test.worldpay.com/wcc/purchase?cartId=6789&instId=12345&currency=GBP&amount=12.00&testMode=100&desc=')
    
