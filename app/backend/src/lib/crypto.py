#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, uuid, time, base64, json
from cryptography.fernet import Fernet
import redis

class Crypto:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis = redis.Redis.from_url(redis_url)

    def generate_key(self):
        """
        Generate a fresh Fernet key. This key will be use
        to encrypt and decrypt the files.
        """
        return Fernet.generate_key()

    def encrypt_file(self, file_data: bytes, user_id: str):
        """
        Here the file is encrypted using the user's key. The token is the result of cipher 
        and authenticate file_data in only one step. This token includes>
         - Random iv of 16 bytes
         - PKCS7 padding
         - HMAC-SHA256
         - Plaintext timestamp 
        """
        key = self.generate_key()
        f = Fernet(key)
        token = f.encrypt(file_data)

        # Fragmentation in 1MB chuncks
        fragment_size = 1024*1024
        fragments = []
        """
        Here we split the generated token into smaller fragments. Each fragment is stored in
        redis with a unique identifier. The fragments are stored in a list, and the file metadata
        is stored in a hash. The metadata includes the user_id, the key, and the created_at timestamp.
        """
        for idx in range(0, len(token), fragment_size):
            frag = token[idx:idx+fragment_size]
            frag_id = str(uuid.uuid4())
            fragments.append((frag_id, frag, idx//fragment_size))

        file_id = str(uuid.uuid4())
        # Push file metada to redis
        self.redis.hset(f"file:{file_id}", mapping={
            "user_id": user_id,
            "key": key.decode(),
            "created_at": str(int(time.time()))
        })

        # List with the fragments of the file
        self.redis.rpush(f"file:{file_id}:fragments", *[f[0] for f in fragments])

        # Store each fragment in redis
        for frag_id, frag_data, index in fragments:
            self.redis.set(f"fragment:{file_id}:{index}", frag_data)

        return {"file_id": file_id, "fragment_ids": [f[0] for f in fragments]}

    def decrypt_file(self, file_id: str, user_id: str) -> bytes:
        """
        Decrypt a file using the user's key. The file is stored in fragments in redis.
        The fragments are retrieved and concatenated to form the original file. The key is
        retrieved from the file metadata. The file metadata includes the user_id, the key,
        and the created_at timestamp.
        """
        meta = self.redis.hgetall(f"file:{file_id}")
        if not meta or meta[b"user_id"].decode() != user_id:
            raise KeyError("No access or not found")

        key = meta[b"key"]
        # Obtener IDs de fragmentos
        frag_ids = self.redis.lrange(f"file:{file_id}:fragments", 0, -1)

        # Recuperar fragmentos y ordenarlos por índice
        data_chunks = []
        """
        Here we retrieve the fragments from redis using the fragment IDs. The fragments are
        sorted by their index to ensure that they are in the correct order. The fragments are
        concatenated to form the original file. The key is used to decrypt the file.
        """
        for fid in frag_ids:
            idx = int(fid.decode().split(":")[-1])
            chunk = self.redis.get(f"fragment:{file_id}:{idx}")
            data_chunks.append((idx, chunk))
        data_chunks.sort(key=lambda x: x[0])
        token = b"".join([c[1] for c in data_chunks])

        # Decrypt the file using the key and the token
        f = Fernet(key)
        return f.decrypt(token)
