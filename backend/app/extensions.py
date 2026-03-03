from flask import request
from flask_limiter import Limiter

from app.utils.request_context import get_client_ip


def _rate_limit_key():
    return get_client_ip(request)


limiter = Limiter(
    key_func=_rate_limit_key,
    default_limits=[],
)
