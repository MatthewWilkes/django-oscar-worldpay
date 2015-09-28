=================================
Worldpay package for django-oscar
=================================

.. image:: https://travis-ci.org/MatthewWilkes/django-oscar-worldpay.png
    :alt: Continuous integration status
    :target: http://travis-ci.org/#!/MatthewWilkes/django-oscar-worldpay

.. image:: https://coveralls.io/repos/MatthewWilkes/django-oscar-worldpay/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/MatthewWilkes/django-oscar-worldpay?branch=master

This package provides integration between django-oscar_ and Worldpay Select Junior (also known as HTML Redirect).

.. _django-oscar: https://github.com/tangentlabs/django-oscar

These payment options can be used individually or together.  Further, the
package is structured so that it can be used without Oscar if you so wish.

.. _`Continuous integration status`: http://travis-ci.org/#!/matthewwilkes/django-oscar-worldpay?branch=master

Current status
--------------

We believe this product is usable in production, but as always, it is released as-is without warranty. If you find any bugs please submit either a
bug report or a pull request.

Security
--------

This package supports the so-called 'MD5 Encryption' security of Worldpay, with configurable fields. It also implement the DNS based checking of
response callbacks.

It uses C_Parameters internally for passing cart information back, this uses a SHA-based HMAC for verification.

This package doesn't yet support the `callbackPW` parameter, patches to add this would be very welcome.

Configuration
-------------

The following parameters should be set:

    * WORLDPAY_INSTANCE_ID
        A string containing your instance ID, such as '12345'
        
    * WORLDPAY_TEST_MODE
        A boolean to determine test mode

    * WORLDPAY_MD5_SECRET
        The string entered in the MD5 field of WorldPay's console, or None
        
    * WORLDPAY_SIGNATURE_FIELDS
        A tuple of field names, such as ('instId', 'cartId', 'amount', 'currency'), to use with the MD5 Secret

    * WORLDPAY_REMOTE_ADDRESS_HEADER
        A string pointing to the key in Request.META that contains the IP of the request's origin.
        Usually either `REMOTE_ADDR` or `HTTP_X_FORWARDED_FOR`.

Gotchas
-------

Worldpay's recommended authentication of requests is based on multiple DNS lookups. Please be sure you have a working and reliable DNS setup
before using this package. Patches to make this lookup optional and to add the `CallbackPW` alternative would be welcome.

You also need the dynamic callback response parameter to be enabled. Currently there are two callbacks, a fail and a success callback. If these
two were integrated this requirement could be dropped.

License
-------

The package is released under the `New BSD license`_.

.. _`New BSD license`: https://github.com/matthewwilkes/django-oscar-worldpay/blob/master/LICENSE

Contributing
------------

Please let `@matthewwilkes`_ know if you use this package, feedback would be very useful. Pull requests are very much welcome, please don't
hesitate to send them. If they're not attended to quickly, ping `@matthewwilkes` on twitter or GitHub. 

Support
-------

Having problems or got a question?

* Have a look at the sandbox site as this is a sample Oscar project
  integrated with Worldpay.  See the contributing guide within the
  docs for instructions on how to set up the sandbox locally.

* Ping `@matthewwilkes`_ (or `@django_oscar`_) with quick queries.

* Ask more detailed questions on the Oscar mailing list: `django-oscar@googlegroups.com`_

* Use Github_ for submitting issues and pull requests.

.. _`@django_oscar`: https://twitter.com/django_oscar
.. _`@matthewwilkes`: https://twitter.com/matthewwilkes
.. _`django-oscar@googlegroups.com`: https://groups.google.com/forum/?fromgroups#!forum/django-oscar
.. _`Github`: http://github.com/MatthewWilkes/django-oscar-worldpay

Changelog
---------

1.2
---

* Nothing yet

1.1
---

* Fix a bug when phonenumber wasn't set.
* Remove some old PayPal references that were missed.

1.0
---

* Initial release. Working integration of Worldpay and Oscar.

0.1
~~~

* Skeleton of Worldpay integration, supporting making requests and receiving callbacks.

0.0
~~~
* Forked from django-oscar-paypal 0.9.5
