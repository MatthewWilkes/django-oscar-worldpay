=================================
Worldpay package for django-oscar
=================================

.. image:: https://travis-ci.org/MatthewWilkes/django-oscar-worldpay.png
    :alt: Continuous integration status
    :target: http://travis-ci.org/#!/MatthewWilkes./django-oscar-worldpay

.. image:: https://coveralls.io/repos/MatthewWilkes/django-oscar-worldpay/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/MatthewWilkes/django-oscar-worldpay?branch=master

This package provides integration between django-oscar_ and Worldpay Select Junior.

.. _django-oscar: https://github.com/tangentlabs/django-oscar

These payment options can be used individually or together.  Further, the
package is structured so that it can be used without Oscar if you so wish.

.. _`Continuous integration status`: http://travis-ci.org/#!/matthewwilkes/django-oscar-worldpay?branch=master

Current status
--------------

This package is not yet suitable for use. It is under active development.
Specifically, the following features are missing:

* Shared passwords
* Dynamic payment responses
* Validation of HMACs for internal parameters

Only once these are in place will the package be usable.

Configuration
-------------

The following parameters should be set:

    * WORLDPAY_INSTANCE_ID
        A string containing your instance ID, such as '12345'
        
    * WORLDPAY_TEST_MODE
        A boolean to determine test mdoe

    * WORLDPAY_MD5_SECRET
        The string entered in the MD5 field of WorldPay's console, or None
        
    * WORLDPAY_SIGNATURE_FIELDS
        A tuple of field names, such as ('instId', 'cartId', 'amount', 'currency')


License
-------

The package is released under the `New BSD license`_.

.. _`New BSD license`: https://github.com/matthewwilkes/django-oscar-worldpay/blob/master/LICENSE

Support
-------

Having problems or got a question?

* Have a look at the sandbox site as this is a sample Oscar project
  integrated with Worldpay.  See the contributing guide within the
  docs for instructions on how to set up the sandbox locally.

* Ping `@matthewwilkes`_ or `@django_oscar`_ with quick queries.

* Ask more detailed questions on the Oscar mailing list: `django-oscar@googlegroups.com`_

* Use Github_ for submitting issues and pull requests.

.. _`@django_oscar`: https://twitter.com/django_oscar
.. _`@matthewwilkes`: https://twitter.com/matthewwilkes
.. _`django-oscar@googlegroups.com`: https://groups.google.com/forum/?fromgroups#!forum/django-oscar
.. _`Github`: http://github.com/MatthewWilkes/django-oscar-worldpay

Changelog
---------

0.1
~~~

* Skeleton of Worldpay integration, supporting making requests and receiving callbacks.

0.0
~~~
* Forked from django-oscar-paypal 0.9.5
