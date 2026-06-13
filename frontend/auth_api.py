import os
import time
from typing import Any, Dict

import requests

API_BASE_URL = os.getenv("CLOUDSEC_API_URL", "https://cloudsec-rag-agent.onrender.com").rstrip("/")
HEALTH_RETRY_DELAYS = [0.5, 1.0]
AUTH_RETRY_DELAYS = [0.5]


def check_backend_health() -> bool:
    """Send a fast, non-blocking check to verify if the backend is awake."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def wait_for_backend(timeout: int = 5) -> None:
    """Wake the backend before auth requests, fast-pathing if already awake."""
    last_error: Exception | None = None

    for attempt, delay in enumerate(HEALTH_RETRY_DELAYS):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=timeout)
            response.raise_for_status()
            return
        except requests.RequestException as exc:
            last_error = exc
            if attempt == len(HEALTH_RETRY_DELAYS) - 1:
                break
            time.sleep(delay)

    raise last_error if last_error is not None else RuntimeError("Backend health check failed.")


def _post_with_retry(path: str, payload: Dict[str, Any], timeout: int = 15) -> requests.Response:
    # Fast post request, assuming backend is verified awake.
    last_error: Exception | None = None

    for attempt, delay in enumerate(AUTH_RETRY_DELAYS):
        try:
            return requests.post(
                f"{API_BASE_URL}{path}",
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            last_error = exc
            if attempt == len(AUTH_RETRY_DELAYS) - 1:
                break
            time.sleep(delay)

    raise last_error if last_error is not None else RuntimeError("Request failed without an error.")


def signup_user(email: str, password: str) -> Dict[str, Any]:
    wait_for_backend()
    response = _post_with_retry(
        "/signup",
        {"email": email, "password": password},
        timeout=45,
    )
    response.raise_for_status()
    return response.json()


def login_user(email: str, password: str) -> Dict[str, Any]:
    wait_for_backend()
    response = _post_with_retry(
        "/login",
        {"email": email, "password": password},
        timeout=45,
    )
    response.raise_for_status()
    return response.json()


def ask_agent(
    query: str,
    attachments: list[dict],
    token: str,
    timeout: int = 180,
    history: list[dict] | None = None,
) -> Dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/ask",
        json={"query": query, "attachments": attachments, "history": history or []},
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
