#!/usr/bin/env python3

"""
S3 Service Module
-----------------

This module provides a service for storing and retrieving file fragments in an S3 bucket.
It uses the Boto3 library to interact with AWS S3.
"""

import boto3

class S3:
    def __init__(self):
        """
        Initialize the S3 client and set the bucket name.

        Note: Ensure that the AWS credentials are set in the environment variables
        """
        self._s3 = boto3.client("s3")
        self._bucket = "main_storage"

    def store_fragment(self, user_id: str, file_uuid: str, fragment_index: int, data: bytes) -> None:
        """
        Store a file fragment in S3.

        Args:
            file_uuid (str): The UUID of the file.
            fragment_index (int): The index of the fragment.
            data (bytes): The data to be stored.
        """
        key = f"{user_id}/{file_uuid}/{fragment_index}.bin"
        self._s3.put_object(Bucket=self.bucket, Key=key, Body=data)

    def get_fragment(self, user_id: str, file_uuid: str, fragment_index: int) -> bytes:
        """
        Retrieve a file fragment from S3.

        Args:
            file_uuid (str): The UUID of the file.
            fragment_index (int): The index of the fragment.

        Returns:
            bytes: The data of the fragment.

        Raises:
            Exception: If the fragment is not found in S3.
        """
        key = f"{user_id}/{file_uuid}/{fragment_index}.bin"
        obj = self._s3.get_object(Bucket=self._bucket, Key=key)

        return obj["Body"].read()
