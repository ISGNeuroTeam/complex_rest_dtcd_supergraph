"""
Custom exceptions.
"""

from rest_framework.exceptions import APIException


class LoadingError(APIException):
    """Failed to convert data to content."""

    status_code = 400
    default_detail = "Cannot convert data to content."
    default_code = "error"


class ManagerError(APIException):
    status_code = 400
    default_detail = "Manager error."
    default_code = "error"
