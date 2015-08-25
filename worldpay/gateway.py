from __future__ import unicode_literals
import socket
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


def build_payment_url(instance_id, cart_id, total, currency, test_mode=False):
    data = (
        ('instId',      instance_id),
        ('cartId',      cart_id),
        ('currency',    currency),
        ('amount',      total),
        ('desc',        ''),
    )
    if test_mode:
        data += ('testMode', 100),
        base = "https://secure-test.worldpay.com/wcc/purchase?"
    else:
        base = "https://secure.worldpay.com/wcc/purchase?"
    
    return base + urlencode(data)


def confirm(request):
    return {}

def check_ip(ip):
    """Check if an IP address has a reverse DNS that matches worldpay.com, and if
    it does, check that that hostname has the IP as one of its resolvables."""
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
    except socket.herror:
        # No reverse DNS available
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
