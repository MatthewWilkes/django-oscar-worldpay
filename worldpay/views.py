from __future__ import unicode_literals
from decimal import Decimal
import json
import logging

from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import View
from oscar.apps.payment.exceptions import UnableToTakePayment
from oscar.apps.checkout.views import OrderPlacementMixin
from oscar.core.loading import get_class, get_model

from oscar.apps.payment.exceptions import RedirectRequired
from oscar.apps.payment.exceptions import PaymentError

from .facade import build_payment_url, confirm

# Load views dynamically
OscarPaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')

BillingAddress = get_model('order', 'BillingAddress')
ShippingAddress = get_model('order', 'ShippingAddress')
Country = get_model('address', 'Country')
Basket = get_model('basket', 'Basket')
Repository = get_class('shipping.repository', 'Repository')
Applicator = get_class('offer.utils', 'Applicator')
Order = get_model('order', 'Order')
Selector = get_class('partner.strategy', 'Selector')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')

logger = logging.getLogger('worldpay')


class SuccessView(OrderPlacementMixin, View):
    """
    Handle a successful sale
    """
    
    def get(self, request, *args, **kwargs):
        order_number = self.checkout_session.get_order_number()
        # Flush all session data
        self.checkout_session.flush()

        # Save order id in session so thank-you page can load it
        order = Order.objects.get(number=order_number)
        self.request.session['checkout_order_id'] = order.id

        response = HttpResponseRedirect(self.get_success_url())
        self.send_signal(self.request, response, order)
        return response
    

class FailView(OrderPlacementMixin, View):
    """
    Handle a failed sale
    """
    
    def get(self, request, *args, **kwargs):
        # Flush all session data
        if 'error' in request.GET:
            messages.error(self.request, request.GET['error'])
        self.restore_frozen_basket()
        return HttpResponseRedirect(reverse('checkout:preview'))
    

class CallbackResponseView(OrderPlacementMixin, View):
    """
    Handle the response from WorldPay
    """
    def post(self, request, *args, **kwargs):
        try:
            data = confirm(request)
        except PaymentError as e:
            #messages.error(self.request, str(e))
            #self.restore_frozen_basket()
            return TemplateResponse(request, 'worldpay/worldpay_response.html', {'url': self.request.build_absolute_uri(reverse("worldpay-fail") + "?error=%s" % str(e))})

        basket = Basket.objects.get(pk=data['M_basket'])
        basket.strategy = Selector().strategy()
        
        if data['M_user'] == 'None':
            user = AnonymousUser()
        else:
            user = User.objects.get(pk=data['M_user'])
        
        # Fetch submission data out of session
        order_number = data['cartId']
        total = Decimal(data['amount'])
        
        # Record payment source
        source_type, is_created = SourceType.objects.get_or_create(name='WorldPay')
        source = Source(source_type=source_type,
                        currency=data['currency'],
                        amount_allocated=total,
                        amount_debited=total,
                        reference=data['transId'])
        self.add_payment_source(source)
        self.add_payment_event('paid', total, reference=data['transId'])
        
        shipping_address = ShippingAddress.objects.get(pk=data['M_shipping_address'])
        if data['M_billing_address'] == 'None':
            billing_address = None
        else:
            billing_address = BillingAddress.objects.get(pk=data['M_billing_address'])
        
        shipping_methods = Repository().get_shipping_methods(basket, user=user, shipping_addr=shipping_address)
        shipping_method = [method for method in shipping_methods if method.code == data['M_shipping_method']][0]
        
        order_kwargs = json.loads(data['M_order_kwargs'])
        # Place order
        calc_total = self.get_order_totals(basket, shipping_method.calculate(basket))
        result = self.handle_order_placement(
            order_number,
            user,
            basket,
            shipping_address,
            shipping_method,
            shipping_method.calculate(basket),
            billing_address,
            calc_total,
            **order_kwargs
        )
        return TemplateResponse(request, 'worldpay/worldpay_response.html', {'url': self.request.build_absolute_uri(reverse("worldpay-success"))})
        
    

class PaymentDetailsView(OscarPaymentDetailsView):
    template_name_preview = 'worldpay/preview.html'

    def get_context_data(self, **kwargs):
        kwargs['WORLDPAY_INSTANCE_ID'] = settings.WORLDPAY_INSTANCE_ID
        data = super(PaymentDetailsView, self).get_context_data(**kwargs)
        return data
    
    def handle_payment(self, order_number, total, **kwargs):
        """
        Complete payment with WorldPay. This redirects into the WorldPay flow.
        """
        data = self.get_context_data()
        shipping_method = data['shipping_method']

        shipping_address = data['shipping_address']
        billing_address = data['billing_address']
        
        M_params = {b'order_kwargs': json.dumps(data['order_kwargs']).encode("utf-8")}
        
        url = build_payment_url(total, order_number, data['user'], data['basket'], shipping_method, shipping_address, billing_address, M_params=M_params, test_mode=settings.WORLDPAY_TEST_MODE)
        
        callback_url = self.request.build_absolute_uri(reverse('worldpay-callback'))
        url += '&MC_Callback=' + callback_url
        raise RedirectRequired(url)
        
