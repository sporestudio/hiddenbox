#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid 
from datetime import datetime   
from typing import List, Dict, Any
from cryptography.fernet import Fernet

class Crypto:
    _FRAGMENT_SIZE = 1024 ** 2 # 1MB

    def __init__(self, key):
        self.__key = key 
        self.__cipher = Fernet(self.__key)

    def _fragment_token(self, token: bytes) -> List[Dict[str, Any]]:
        """
        Fragment a tokenized (encrypted) file into smaller chunks. Each chunk is represented as a dictionary.

        Args:
            token (bytes): The file encrypted using Fernet's token format.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing:
                - uuid (str): A unique identifier for the fragment.
                - data (bytes): The fragment data.
                - index (int): The index of the fragment in the original file.
        """
        fragments = []

        for idx in range(0, len(token), self._FRAGMENT_SIZE):
            frag = {
                "uuid": str(uuid.uuid4()),
                "data": token[idx:idx+self._FRAGMENT_SIZE],
                "index": idx // self._FRAGMENT_SIZE
            }
            fragments.append(frag)
        
        return fragments

    def encrypt_file(self, file_data: bytes, user_id: str) -> Dict[str, Any]:
        """
        Encrypt a file and associate it with the user's ID. The file is fragmented into smaller chunks.
        
        Args:
            file_data (bytes): The file data to be encrypted.
            user_id (str): The user ID of the owner.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - file_uuid (str): A unique identifier for the file
                - user_id (str): The user ID of the owner
                - key (str): The key used to encrypt the file
                - created_at (str): The timestamp when the file was created
                - fragments (List[Dict[str, Any]]): A list of fragments of the encrypted file
        """
        token = self.__cipher.encrypt(file_data)  # Encrypt the file data as a Fermet's token format
        fragments = self._fragment_file(token)
        file_uuid = str(uuid.uuid4())

        encrypted_file = {
            "file_uuid": file_uuid,
            "user_id": user_id,
            "key": self._key.decode(),
            "created_at": str(int(datetime.timezone.utc.timestamp())),
            "fragments": fragments
        }

        return encrypted_file
    
    def decrypt_fragmented_file(self, fragments: List[Dict[str, Any]]) -> bytes:
        """
        Decrypt a fragmented file. The fragments are combined into a single byte string and then decrypted.

        Args:
            fragments (List[Dict[str, Any]]): The list of fragments to be decrypted.
        
        Returns:
            bytes: The decrypted file data.
        """
        sorted_fragments = sorted(fragments, key=lambda x: x["index"])  # Sort fragments by index
        token = b"".join([frag["data"] for frag in sorted_fragments])

        return self.__cipher.decrypt(token)
