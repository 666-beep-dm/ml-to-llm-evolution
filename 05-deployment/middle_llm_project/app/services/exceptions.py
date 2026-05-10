"""Domain-specific exceptions raised by the LLM service."""


class LLMServiceError(Exception):
    """Base class for all LLM service errors."""

    user_message: str = "An unexpected error occurred while contacting the AI model."
    status_code: int = 500


class LLMTimeoutError(LLMServiceError):
    """The request to the LLM timed out."""

    def __init__(self, timeout: float) -> None:
        self.user_message = (
            f"The AI model did not respond within {timeout:.0f} seconds. "
            "Please try again."
        )
        self.status_code = 504
        super().__init__(self.user_message)


class LLMRateLimitError(LLMServiceError):
    """OpenAI rate limit was reached."""

    user_message = (
        "The AI service is currently overloaded. "
        "Please wait a moment and try again."
    )
    status_code = 429


class LLMEmptyResponseError(LLMServiceError):
    """The model returned an empty or blank response."""

    user_message = (
        "The AI model returned an empty response. "
        "Please rephrase your question and try again."
    )
    status_code = 502


class LLMAPIError(LLMServiceError):
    """Any other API-level error from OpenAI."""

    def __init__(self, status_code: int, message: str) -> None:
        self.user_message = "The AI service returned an unexpected error."
        self.status_code = 502
        super().__init__(message)
