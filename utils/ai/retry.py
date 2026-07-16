import time


def should_retry(exception: Exception) -> bool:
    """
    Return True only for temporary AI service errors.
    """

    error = str(exception).lower()

    retry_errors = (
        "429",
        "500",
        "502",
        "503",
        "504",
        "timeout",
        "timed out",
        "temporarily unavailable",
        "resource_exhausted",
        "service unavailable",
        "internal server error",
        "deadline exceeded"
    )

    return any(keyword in error for keyword in retry_errors)


def wait_before_retry(attempt: int):
    """
    Wait before retrying using exponential backoff.

    Attempt 1 -> 2 seconds
    Attempt 2 -> 4 seconds
    Attempt 3 -> 8 seconds
    """

    delay = 2 ** attempt

    print(f"Retrying AI request in {delay} second(s)...")

    time.sleep(delay)