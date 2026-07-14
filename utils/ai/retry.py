import time


def should_retry(exception: Exception) -> bool:
    """
    Check whether the AI request should be retried.
    """

    error = str(exception).lower()

    retry_errors = [
        "503",
        "429",
        "timeout",
        "temporarily unavailable",
        "resource_exhausted"
    ]

    return any(item in error for item in retry_errors)


def wait_before_retry(seconds: int = 3):
    """
    Wait before retrying the request.
    """

    time.sleep(seconds)