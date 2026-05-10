"""
Domain exception hierarchy.
Open/Closed: add new exception types without modifying handlers.
"""


class RAGException(Exception):
    """Base exception for all domain errors."""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"


class DocumentNotFoundError(RAGException):
    status_code = 404
    error_code = "DOCUMENT_NOT_FOUND"


class UnsupportedFileTypeError(RAGException):
    status_code = 415
    error_code = "UNSUPPORTED_FILE_TYPE"


class FileTooLargeError(RAGException):
    status_code = 413
    error_code = "FILE_TOO_LARGE"


class VectorStoreError(RAGException):
    status_code = 503
    error_code = "VECTOR_STORE_ERROR"


class LLMError(RAGException):
    status_code = 502
    error_code = "LLM_ERROR"


class ExtractionError(RAGException):
    status_code = 422
    error_code = "EXTRACTION_ERROR"
