#!/usr/bin/env python3

"""
S3 Service Module
-----------------

This module provides a service for storing and retrieving file fragments in an S3 bucket.
It uses the Boto3 library to interact with AWS S3.
"""

import os

import boto3
from dotenv import load_dotenv
from .exceptions import BucketNotDefined, FragmentNotFound, S3OperationFailed
from lib.datatypes import EncryptedFile, FileFragment

load_dotenv()

class S3:
    def __init__(self):
        """
        Initialize the S3 client and set the bucket name.

        Note: Ensure that the AWS credentials are set in the environment variables
        """
        self._s3 = boto3.client("s3")
        _bucket = os.getenv("S3_BUCKET_NAME")

        if _bucket is None:
            raise BucketNotDefined()
        
        self._bucket = _bucket

    def store_fragment(self, user_id: str, encrypted: EncryptedFile, fragment: FileFragment) -> None:
        """
        Store a file fragment in S3.

        Args:
            file_uuid (str): The UUID of the file.
            fragment_index (int): The index of the fragment.
            data (bytes): The data to be stored.
        """
        key = f"{user_id}/{encrypted.uuid}/{fragment.index}.bin"
        print(f"Storing fragment at key: {key}")

        try:
            self._s3.put_object(Bucket=self._bucket, Key=key, Body=fragment.data)

        except Exception as e:
            print(f"Error uploading to S3: {e}")
            print(f"Bucket: {self._bucket}, Key: {key}")
            raise S3OperationFailed(operation="put_object") from e

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
        if not isinstance(fragment_index, int):
            raise TypeError(f"Invalid fragment index: {fragment_index}")

        key = f"{user_id}/{file_uuid}/{fragment_index}.bin"
        
        try:
            obj = self._s3.get_object(Bucket=self._bucket, Key=key)
            return obj["Body"].read()
        
        except self._s3.exceptions.NoSuchKey:
            raise FragmentNotFound(fragment_key=key)
        except Exception as e:
            raise S3OperationFailed(operation="get_object") from e
