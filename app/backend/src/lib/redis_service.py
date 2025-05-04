#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis


class RedisService:
    def __init__(self, url):
        self._redis = redis.Redis.from_url(url)

    def save_metadata(self, file_uuid: str, user_id: str, key: str, created_at: str) -> None :
        self._redis.hset(f"file:{file_uuid}", mapping={
            "user_id": user_id,
            "key": key,
            "created_at": created_at
        })

    def save_fragments(self, file_uuid: str, fragments: list) -> None:
        self._redis.rpush(f"file:{file_uuid}:fragments", *[str(idx) for idx, _ in fragments])
        for idx, frag in fragments:
            self._redis.set(f"fragment:{file_uuid}:{idx}", frag)

    def load_metadata(self, file_uuid: str) -> dict:
        data = self._redis.hgetall(f"file:{file_uuid}")
        if not data:
            return {}
        return {k.decode(): v.decode() for k,v in data.items()}
    
    def load_fragments(self, file_uuid: str) -> list:
        idxs = self._redis.lrange(f"file{file_uuid}:fragments", 0, -1)
        result = []
        for binary_idx in idxs:
            idx = int(binary_idx.decode())
            frag = self._redis.get(f"fragment:{file_uuid}:{idx}")
            result.append(idx, frag)
        return result
