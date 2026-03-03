from ipaddress import ip_address

from flask import current_app


def _normalized_ip(value):
    if not value:
        return None
    candidate = str(value).strip()
    if not candidate:
        return None
    try:
        ip_address(candidate)
    except ValueError:
        return None
    return candidate


def get_client_ip(req):
    """
    Resolve caller identity IP.
    By default, ignore proxy headers to prevent client-side spoofing.
    """
    if current_app.config.get('TRUST_PROXY_HEADERS', False):
        xff = req.headers.get('X-Forwarded-For', '')
        if xff:
            first = xff.split(',')[0].strip()
            ip = _normalized_ip(first)
            if ip:
                return ip

        x_real_ip = _normalized_ip(req.headers.get('X-Real-IP', ''))
        if x_real_ip:
            return x_real_ip

    remote = _normalized_ip(req.remote_addr)
    return remote or 'unknown'
