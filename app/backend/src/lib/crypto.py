#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime   
import os, uuid, time, base64, json
from typing import List, Dict, Any
from cryptography.fernet import Fernet
import redis

class Crypto:
    _FRAGMENT_SIZE = 1024 ** 2 # 1MB

    def __init__(self, key: bytes = None, redis_url="redis://localhost:6379/0"):
        self._key = key if key else self.generate_key()
        self._cipher = Fernet(self._key)
        self.redis = redis.Redis.from_url(redis_url)

    def generate_key(self) -> bytes:
        """
        Generate a fresh Fernet key. This key will be use
        to encrypt and decrypt the files.

        Returns:
            bytes: A base64-encoded 32-bytes key.
        """
        return Fernet.generate_key()
    
    def _fragment_token(self, token: bytes) -> List[Dict[str, Any]]:
        """
        Fragment a file into smaller chunks. Each chunk is stored in a dictionary.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing:
                - "id": A unique identifier for the fragment
                - "data": The fragment data
                - "index": The index of the fragment in the original file
        """
        fragments = []

        for idx in range(0, len(token), self._FRAGMENT_SIZE):
            frag = {
                "id": str(uuid.uuid4()),
                "data": token[idx:idx+self._FRAGMENT_SIZE],
                "index": idx // self._FRAGMENT_SIZE
            }
            fragments.append(frag)
        
        return fragments

    def encrypt_file(self, file_data: bytes, user_id: str) -> Dict[str, Any]:
        """
        Here the file is encrypted using the user's key. The token is the result of cipher 
        and authenticate file_data in only one step. This token includes:
            - Random iv of 16 bytes
            - PKCS7 padding
            - HMAC-SHA256
            - Plaintext timestamp 
        
        Args:
            file_data (bytes): The file data to be encrypted.
            user_id (str): The user ID of the owner.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - "file_id": A unique identifier for the file
                - "user_id": The user ID of the owner
                - "key": The key used to encrypt the file
                - "created_at": The timestamp when the file was created
                - "fragments": A list of fragments of the encrypted file
        """
        token = self._cipher.encrypt(file_data)
        fragments = self._fragment_file(token)
        file_id = str(uuid.uuid4())

        encrypted_file = {
            "file_id": file_id,
            "user_id": user_id,
            "key": self._key.decode(),
            "created_at": str(int(datetime.timezone.utc.timestamp())),
            "fragments": fragments
        }

        return encrypted_file

        # # Push file metada to redis
        # self.redis.hset(f"file:{file_id}", mapping={
        #     "user_id": user_id,
        #     "key": self._key.decode(),
        #     "created_at": str(int(time.time()))
        # })

        # # List with the fragments of the file
        # self.redis.rpush(f"file:{file_id}:fragments", *[f["id"] for f in fragments])

        # # Store each fragment in redis
        # for frag_id, frag_data, index in fragments:
        #     self.redis.set(f"fragment:{file_id}:{index}", frag_data)

        # return {"file_id": file_id, "fragment_ids": [f[0] for f in fragments]}

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

        # Obtain fragment IDs from redis
        frag_ids = self.redis.lrange(f"file:{file_id}:fragments", 0, -1)

        # Recover the fragments and sort them by index
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
