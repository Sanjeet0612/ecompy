class AIError(Exception):
    """
    Base exception for all AI related errors.
    """
    pass


class AIConnectionError(AIError):
    """
    Failed to connect with AI provider.
    """
    pass


class AIResponseError(AIError):
    """
    AI returned an invalid response.
    """
    pass


class AIParseError(AIError):
    """
    Unable to parse AI response.
    """
    pass


class AIValidationError(AIError):
    """
    AI response validation failed.
    """
    pass


class AIQuotaExceededError(AIError):
    """
    AI quota or rate limit exceeded.
    """
    pass


class AIRetryLimitExceededError(AIError):
    """
    Maximum retry limit exceeded.
    """
    pass