from django.conf.urls import *
from django.views.decorators.csrf import csrf_exempt

from worldpay import views


urlpatterns = patterns('',
    # Override for basket preview that adds the worldpay form
    url(r'preview/$',
        views.PaymentDetailsView.as_view(preview=True),
        name='worldpay-preview'),
    
    # Callback
    url(r'callback$', csrf_exempt(views.CallbackResponseView.as_view()),
        name='worldpay-callback'),

    url(r'success$', views.SuccessView.as_view(),
        name='worldpay-success'),
    url(r'fail$', views.FailView.as_view(),
        name='worldpay-fail'),
    
)
