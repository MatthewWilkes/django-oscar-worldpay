from django.conf.urls import *
from django.views.decorators.csrf import csrf_exempt

from worldpay import views


urlpatterns = patterns('',
    # Override for basket preview that adds the worldpay form
    url(r'preview/$',
        views.SuccessResponseView.as_view(preview=True),
        name='worldpay-preview'),
    
    # Callback
    url(r'callback/(?P<basket_id>\d+)/$', views.CallbackResponseView.as_view(),
        name='worldpay-callback'),
    
    url(r'place-order/(?P<basket_id>\d+)/$', views.SuccessResponseView.as_view(),
        name='worldpay-place-order'),
)
