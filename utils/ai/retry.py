import time


def should_retry(exception: Exception) -> bool:
    """
    Retry only for temporary server/network errors.
    Never retry for quota, authentication, or invalid request errors.
    """

    error = str(exception).lower()

    # Non-retryable errors
    non_retry_errors = (
        "quota exceeded",
        "resource_exhausted",
        "invalid api key",
        "api key not valid",
        "permission denied",
        "unauthenticated",
        "unauthorized",
        "forbidden",
        "not found",
        "invalid argument",
        "bad request",
        "model not found",
        "unsupported model",
        "billing",
    )

    if any(keyword in error for keyword in non_retry_errors):
        return False

    # Retry only for temporary failures
    retry_errors = (
        "500",
        "502",
        "503",
        "504",
        "timeout",
        "timed out",
        "service unavailable",
        "temporarily unavailable",
        "internal server error",
        "deadline exceeded",
        "connection reset",
        "connection aborted",
        "connection refused",
        "network error",
    )

    return any(keyword in error for keyword in retry_errors)


def wait_before_retry(attempt: int):
    """
    Exponential backoff.

    Attempt 1 -> 2 sec
    Attempt 2 -> 4 sec
    Attempt 3 -> 8 sec
    """

    delay = min(2 ** attempt, 8)

    print(f"Retrying AI request in {delay} second(s)...")

    time.sleep(delay)