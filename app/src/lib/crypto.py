#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, uuid, base64, json
from cryptography.fernet import Fernet
import redis 

class Crypto:
    def __init__(self, redis_url):
        self.redis = redis.Redis.from_url(redis_url)

    def generate_key(self):
        """
        Generate a new Fernet key and store it in Redis.
        """
        return Fernet.generate_key()
    
    def encrypt(self, file_data: bytes, user_id: str):
        """
        Encrypt the file data using the user's key.
        """
        key = self.generate_key()
        f = Fernet(key)