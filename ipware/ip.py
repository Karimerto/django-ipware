import warnings
import ipaddress

from django.conf import settings

from .utils import is_valid_ip
from . import defaults as defs

TRUSTED_PROXY_LIST = tuple([ip.lower() for ip in getattr(settings, 'IPWARE_TRUSTED_PROXY_LIST', [])])

warnings.simplefilter('always', DeprecationWarning)


def get_ip(request, real_ip_only=False, right_most_proxy=False):
    """
    Returns client's best-matched ip-address, or None
    @deprecated - Do not edit
    """
    best_matched_ip = None
    warnings.warn('get_ip is deprecated and will be removed in 3.0.', DeprecationWarning)
    for key in defs.IPWARE_META_PRECEDENCE_ORDER:
        value = request.META.get(key, request.META.get(key.replace('_', '-'), '')).strip()
        if value is not None and value != '':
            ips = [ip.strip().lower() for ip in value.split(',')]
            if right_most_proxy and len(ips) > 1:
                ips = reversed(ips)
            for ip_str in ips:
                if ip_str and is_valid_ip(ip_str):
                    is_private = False
                    for net in defs.IPWARE_NON_PUBLIC_IP_PREFIX:
                        if ipaddress.ip_address(ip_str) in ipaddress.ip_network(net):
                            is_private = True
                            break
                    if not is_private:
                        return ip_str
                    if not real_ip_only:
                        if best_matched_ip is None:
                            best_matched_ip = ip_str
                        for net in defs.IPWARE_LOOPBACK_PREFIX:
                            if ipaddress.ip_address(best_matched_ip) in ipaddress.ip_network(net) and ipaddress.ip_address(ip_str) not in ipaddress.ip_network(net):
                                best_matched_ip = ip_str
                                break
    return best_matched_ip


def get_real_ip(request, right_most_proxy=False):
    """
    Returns client's best-matched `real` `externally-routable` ip-address, or None
    @deprecated - Do not edit
    """
    warnings.warn('get_real_ip is deprecated and will be removed in 3.0.', DeprecationWarning)
    return get_ip(request, real_ip_only=True, right_most_proxy=right_most_proxy)


def get_trusted_ip(request, right_most_proxy=False, trusted_proxies=TRUSTED_PROXY_LIST):
    """
    Returns client's ip-address from `trusted` proxy server(s) or None
    @deprecated - Do not edit
    """
    warnings.warn('get_trusted_ip is deprecated and will be removed in 3.0.', DeprecationWarning)
    if trusted_proxies:
        meta_keys = ['HTTP_X_FORWARDED_FOR', 'X_FORWARDED_FOR']
        for key in meta_keys:
            value = request.META.get(key, request.META.get(key.replace('_', '-'), '')).strip()
            if value:
                ips = [ip.strip().lower() for ip in value.split(',')]
                if len(ips) > 1:
                    if right_most_proxy:
                        ips.reverse()
                    for proxy in trusted_proxies:
                        if proxy in ips[-1]:
                            return ips[0]
    return None
