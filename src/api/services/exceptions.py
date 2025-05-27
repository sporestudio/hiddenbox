#!/usr/bin/env python3

"""
S3 Service Exceptions Module
------------------------

This module defines custom exceptions for the S3 service.
It includes exceptions for when the S3 bucket is not defined,
when a file fragment is not found, and when an S3 operation fails.
"""

class BucketNotDefined(Exception):
    """
    Exception raised when the S3 bucket name is not defined.
    """
    def __init__(self, message="The environmental variable 'S3_BUCKET_NAME' must be defined to initialize an S3 instance."):
        self.message = message
        super().__init__(self.message)


class FragmentNotFound(Exception):
    """
    Exception raised when a file fragment is not found in S3.
    """
    def __init__(self, fragment_key, message="The requested fragment was not found in S3."):
        self.fragment_key = fragment_key
        self.message = f"{message} Key: {fragment_key}"
        super().__init__(self.message)


class S3OperationFailed(Exception):
    """
    Exception raised when an S3 operation fails.
    """
    def __init__(self, operation, message="The S3 operation failed."):
        self.operation = operation
        self.message = f"{message} Operation: {operation}"
        super().__init__(self.message)