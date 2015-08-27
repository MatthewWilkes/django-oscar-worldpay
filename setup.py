#!/usr/bin/env python
from setuptools import setup, find_packages

from worldpay import VERSION


setup(
    name='django-oscar-worldpay',
    version=VERSION,
    url='https://github.com/matthewwilkes/django-oscar-worldpay',
    author="Matthew Wilkes",
    author_email="django-oscar-worldpay@matthewwilkes.name",
    description=(
        "Integration with Worldpay payments for django-oscar"),
    long_description=open('README.rst').read(),
    keywords="Payment, WorldPay, Oscar",
    license=open('LICENSE').read(),
    platforms=['linux'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    install_requires=[
        'requests>=1.0',
        'django-localflavor',
        'six',
    ],
    extras_require={
        'oscar': ["django-oscar>=0.6"]
    },
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Other/Nonlisted Topic'],
)
