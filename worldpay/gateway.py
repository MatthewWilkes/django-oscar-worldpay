from __future__ import unicode_literals
import hashlib
import hmac
import logging
import socket
from decimal import Decimal

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from six import binary_type

logger = logging.getLogger("worldpay")


def build_payment_url(instance_id, cart_id, total, currency, worldpay_params=None, M_params=None, secret=None, SignatureFields=None, MD5Secret=None, test_mode=False):
    sane_total = ("{0:.2f}".format(Decimal(total.decode("ascii"))))
    data = (
        (b'instId',      instance_id.decode("ascii")),
        (b'cartId',      cart_id.decode("ascii")),
        (b'currency',    currency.decode("ascii")),
        (b'amount',      sane_total),
        (b'desc',        ''),
    )
    if M_params is not None:
        M_params = sorted((b"M_" + key, value) for (key, value) in M_params.items())
        data += tuple((k, v.decode("utf-8")) for (k, v) in M_params)
        if secret is not None:
            # Generate a HMAC to verify our data is untouched
            if not isinstance(secret, binary_type):
                raise ValueError("Secret must be a bytes object")
            auth = hmac.new(secret, digestmod=hashlib.sha256)
            auth.update(cart_id)
            auth.update(sane_total.encode("utf-8"))
            auth.update(currency)
            params = urlencode(M_params)
            auth.update(params.encode("utf-8"))
            data += (b'M_authenticator', auth.hexdigest()), 
        
    if worldpay_params is not None:
        worldpay_params = sorted(worldpay_params.items())
        data += tuple(worldpay_params)
    
    if SignatureFields is not None and MD5Secret is not None:
        # Add an MD5 hash of the fields specified as a signature
        values = (MD5Secret,) + tuple(map(lambda x:dict(data).get(x).encode('utf-8'), SignatureFields))
        to_hash = b":".join(values)
        data += (b'signature', hashlib.md5(to_hash).hexdigest()),
    
    if test_mode:
        data += (b'testMode', '100'),
        base = "https://secure-test.worldpay.com/wcc/purchase?"
    else:
        base = "https://secure.worldpay.com/wcc/purchase?"
    return base + urlencode([(k,v.encode("utf-8")) for (k,v) in data])


def confirm(request, secret=None):
    if request.POST['transStatus'] != 'Y':
        raise ValueError("Transaction not authorised")
    passed_data = dict(request.POST.items())
    
    M_params = sorted((key, value) for (key, value) in passed_data.items() if key.startswith("M_") and key != 'M_authenticator')
    if secret is not None:
        # Generate a HMAC to verify our data is untouched
        if not isinstance(secret, binary_type):
            raise ValueError("Secret must be a bytes object")
        auth = hmac.new(secret, digestmod=hashlib.sha256)
        auth.update(binary_type(passed_data['cartId'].encode("utf-8")))
        auth.update(binary_type(passed_data['amount'].encode("utf-8")))
        auth.update(binary_type(passed_data['currency'].encode("utf-8")))
        params = urlencode(M_params)
        auth.update(params.encode("utf-8"))
        authenticator = auth.hexdigest()
        if authenticator != passed_data['M_authenticator']:
            logger.warn("Got incorrect authenticator. Expected %s, got %s." % (authenticator, passed_data['M_authenticator']))
            raise ValueError("Transaction details have been tampered with. Aborting.")
    
    return passed_data

def check_ip(ip):
    """Check if an IP address has a reverse DNS that matches worldpay.com, and if
    it does, check that that hostname has the IP as one of its resolvables."""
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
    except socket.herror:
        # No reverse DNS service available
        return False
    except socket.gaierror:
        # No match
        return False
    
    if hostname.endswith(".worldpay.com") or hostname.endswith(".rbsworldpay.com"):
        try:
            # The 80 here is because getaddrinfo is expecting to be used to open
            # sockets. We can ignore the port, we're just interested in the
            # resolved version.
            names = socket.getaddrinfo(hostname, 80)
        except socket.gaierror:
            # Forward DNS lookup error
            return False
        
        for family, type_, proto, canonname, sockaddr in names:
            if sockaddr[0] == ip:
                return True
    
    return False
