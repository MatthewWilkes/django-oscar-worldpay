from __future__ import unicode_literals
import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from oscar.apps.payment.exceptions import UnableToTakePayment
from oscar.apps.checkout.views import OrderPlacementMixin
from oscar.core.loading import get_class, get_model

from oscar.apps.payment.exceptions import RedirectRequired
from oscar.apps.payment.exceptions import PaymentError

from facade import build_payment_url, confirm

# Load views dynamically
OscarPaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')

ShippingAddress = get_model('order', 'ShippingAddress')
Country = get_model('address', 'Country')
Basket = get_model('basket', 'Basket')
Repository = get_class('shipping.repository', 'Repository')
Applicator = get_class('offer.utils', 'Applicator')
Selector = get_class('partner.strategy', 'Selector')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')

logger = logging.getLogger('worldpay')


class CallbackResponseView(OrderPlacementMixin, View):
    """
    Handle the response from WorldPay
    """
    def get(self, request, *args, **kwargs):
        try:
            data = confirm(request)
        except PaymentError as e:
            messages.error(self.request, str(e))
            self.restore_frozen_basket()
            return HttpResponseRedirect(reverse('checkout:payment-details'))

        # Fetch submission data out of session
        order_number = self.checkout_session.get_order_number()
        basket = self.get_submitted_basket()
        total_incl_tax, total_excl_tax = self.get_order_totals(basket)

        # Record payment source
        source_type, is_created = SourceType.objects.get_or_create(name='WorldPay')
        source = Source(source_type=source_type,
                        currency='GBP',
                        amount_allocated=total_incl_tax,
                        amount_debited=total_incl_tax)
        self.add_payment_source(source)

        # Place order
        return self.handle_order_placement(order_number,
                                           basket,
                                           total_incl_tax,
                                           total_excl_tax)
    

class PaymentDetailsView(OscarPaymentDetailsView):
    template_name_preview = 'worldpay/preview.html'

    def get_context_data(self, **kwargs):
        kwargs['WORLDPAY_INSTANCE_ID'] = settings.WORLDPAY_INSTANCE_ID
        data = super(PaymentDetailsView, self).get_context_data(**kwargs)
        data['worldpay_callback'] = self.request.build_absolute_uri(
            reverse('worldpay-callback', kwargs={'basket_id': data['basket'].id})
        )
        return data
    
    def handle_payment(self, order_number, total, **kwargs):
        """
        Complete payment with WorldPay. This redirects into the WorldPay flow.
        """
        url = build_payment_url(order_number)
        raise RedirectRequired(url)
        
