#!/usr/bin/env python

"""
Redis Service Module
--------------------

Redis service for storing and retrieving file metadata and fragments.
This module provides a RedisService class that allows you to store and retrieve
file metadata and fragments in a Redis database. The metadata includes the file's
unique identifier, user ID, encryption key, and creation timestamp. The fragments
are stored as a list of FileFragment objects, which contain the fragment's index
and data.

Usage:

>>> from redis_service import RedisService

>>> # Initialize the Redis service
>>> redis_service = RedisService(url="redis://localhost:6379")

>>> # Store metadata
>>> redis_service.store_metadata(
        file_uuid="1234",
        user_id="user1",
        key="encryption_key",
        created_at="2023-10-01T12:00:00Z"
    )

>>> # Store fragments
>>> fragments = [FileFragment(index=0, data=b"fragment_data_0"), FileFragment(index=1, data=b"fragment_data_1")]
>>> redis_service.store_fragments(file_uuid="1234", fragments=fragments)

>>> # Retrieve metadata
>>> metadata = redis_service.get_metadata(file_uuid="1234")

>>> # Retrieve fragments
>>> retrieved_fragments = redis_service.get_fragments(file_uuid="1234")
"""

import redis

from .datatypes import FileFragment

class RedisService:
    def __init__(self, url):
        self._redis = redis.Redis.from_url(url)

    def store_metadata(self, file_uuid: str, user_id: str, key: str, created_at: str) -> None:
        """
        Save metadata of an encrypted file into Redis database.

        Args:
            file_uuid (str): File's unique identifier
            user_id (str): User's unique identifier
            key (str): Encryption key
            created_at (str): Timestamp of when the file was created
        """
        self._redis.hset(f"file:{file_uuid}", mapping={
            "user_id": user_id,
            "key": key,
            "created_at": created_at
        })

    def store_fragments(self, file_uuid: str, fragments: list) -> None:
        """
        Save a list with the fragments' ids and their respective fragments.

        Args:
            file_uuid (str): File's unique identifier
            fragments (list[FileFragments]): List of FileFragments files objects
        """
        self._redis.rpush(f"file:{file_uuid}:fragments", *[str(f.index) for f in fragments])

        for f in fragments:
            self._redis.set(f"fragment:{file_uuid}:{f.index}", f.data)

    def get_metadata(self, file_uuid: str) -> dict[str, str]:
        """
        Load file metadata from Redis database.

        Args:
            file_uuid (str): File's unique identifier

        Returns:
            dict: A dictionary with the file's metadata. The keys are the field names
                  and the values are the field values.
        """
        data = self._redis.hgetall(f"file:{file_uuid}")

        if not data:
            return {}

        return {k.decode(): v.decode() for k,v in data.items()}

    def get_fragments(self, file_uuid: str) -> list[FileFragment]:
        """
        Get the stored fragments files from Redis database.

        Args:
            file_uuid (str): File's unique identifier

        Returns:
            list[FileFragments]: List of FileFragments files objects
        """
        idxs = self._redis.lrange(f"file:{file_uuid}:fragments", 0, -1)
        result = []

        for binary_idx in idxs:
            idx = int(binary_idx.decode())
            frag_data = self._redis.get(f"fragment:{file_uuid}:{idx}")
            result.append(FileFragment(index=idx, data=frag_data, uuid=file_uuid))

        return result
