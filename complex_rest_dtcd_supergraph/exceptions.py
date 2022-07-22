"""
Custom exceptions.
"""

from rest_framework.exceptions import APIException


class LoadingError(APIException):
    """Failed to convert data to content subgraph."""

    status_code = 400
    default_detail = "Cannot convert data to content subgraph."
    default_code = "error"
