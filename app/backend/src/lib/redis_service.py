#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
from typing import List, Dict

class RedisService:
    def __init__(self, url):
        self._redis = redis.Redis.from_url(url)

    def store_metadata(self, file_uuid: str, user_id: str, key: str, created_at: str) -> None:
        """
        Save metadata of an encrypted file into Redis database.

        Args:
            file_uuid (str): file's unique identifier
            user_id (str): user's unique identifier
            key (str): encryption key
            created_at (str): timestamp of when the file was created
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
            file_uuid (str): file's unique identifier
            fragments (list[FileFragments]): list of FileFragments files objects
        """
        self._redis.rpush(f"file:{file_uuid}:fragments", *[str(f.index) for f in fragments])
    
        for f in fragments:
            self._redis.set(f"fragment:{file_uuid}:{f.index}", f.data)

    def get_metadata(self, file_uuid: str) -> Dict:
        """
        Load file metadata from Redis database.

        Args:
            file_uuid (str): file's unique identifier

        Returns:
            Dict: A dictionary with the file's metadata. The keys are the field names and the values are the field values.
        """
        data = self._redis.hgetall(f"file:{file_uuid}")

        if not data:
            return {}

        return {k.decode(): v.decode() for k,v in data.items()}
    
    def get_fragments(self, file_uuid: str) -> List:
        """
        Get the stored fragments files from Redis database.

        Args:
            file_uuid (str): file's unique identifier

        Returns:
            list[FileFragments]: list of FileFragments files objects
        """
        idxs = self._redis.lrange(f"file:{file_uuid}:fragments", 0, -1)
        result = []

        for binary_idx in idxs:
            idx = int(binary_idx.decode())
            frag_data = self._redis.get(f"fragment:{file_uuid}:{idx}")
            result.append(FileFragment(index=idx, data=frag_data))

        return result
