from datetime import datetime, timedelta
from typing import Optional, Tuple

import streamlit as st

try:
    import extra_streamlit_components as stx
except ImportError:
    stx = None


TOKEN_COOKIE = "cloudsec_auth_token"
EMAIL_COOKIE = "cloudsec_user_email"
COOKIE_TTL_DAYS = 7


def _cookie_manager():
    if stx is None:
        return None
    return stx.CookieManager(key="cloudsec_cookie_manager")


def restore_auth_from_cookie() -> Tuple[Optional[str], Optional[str]]:
    manager = _cookie_manager()
    if manager is None:
        return None, None

    token = manager.get(TOKEN_COOKIE)
    email = manager.get(EMAIL_COOKIE)
    return token, email


def persist_auth_to_cookie(token: str, email: str) -> None:
    manager = _cookie_manager()
    if manager is None:
        return

    expires_at = datetime.utcnow() + timedelta(days=COOKIE_TTL_DAYS)
    manager.set(TOKEN_COOKIE, token, expires_at=expires_at)
    manager.set(EMAIL_COOKIE, email, expires_at=expires_at)


def clear_auth_cookie() -> None:
    manager = _cookie_manager()
    if manager is None:
        return

    # extra-streamlit-components raises KeyError if delete is called for
    # a cookie that does not exist, so guard each delete.
    for cookie_name in (TOKEN_COOKIE, EMAIL_COOKIE):
        try:
            if manager.get(cookie_name) is not None:
                manager.delete(cookie_name)
        except KeyError:
            pass
