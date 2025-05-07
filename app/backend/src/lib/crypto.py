#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid 
from datetime import datetime, timezone   
from .datatypes import FileFragment, EncryptedFile
from cryptography.fernet import Fernet

class Crypto:
    _FRAGMENT_SIZE = 1024 * 1024 # 1MB

    def __init__(self, key):
        self.__key = key 
        self.__cipher = Fernet(self.__key)

    def _fragment_bytes(self, token: bytes) -> list[FileFragment]:
        """
        Fragment a tokenized (encrypted) file into smaller chunks. Each chunk is represented as a dictionary.

        Args:
            token (bytes): The file encrypted using Fernet's token format.

        Returns:
            list[FileFragment]: A list of file fragments. To see FileFragment attributes refer to `datatypes` module documentation.
        """
        fragments = []
        fragment_uuid = str(uuid.uuid4())

        for idx in range(0, len(token), self._FRAGMENT_SIZE):
            frag = FileFragment(
                uuid=fragment_uuid,
                data=token[idx:idx+self._FRAGMENT_SIZE],
                index=(idx // self._FRAGMENT_SIZE)
            )
            fragments.append(frag)
        
        return fragments

    def encrypt(self, file_data: bytes, user_id: str) -> EncryptedFile:
        """
        Encrypt a file and associate it with the user's ID. The file is fragmented into smaller chunks.
        
        Args:
            file_data (bytes): The file data to be encrypted.
            user_id (str): The user ID of the owner.
        
        Returns:
            EncryptedFile: An object representing the encrypted file (data and metadata included). To see EncryptedFile attributes refer to `datatypes` module documentation.
        """
        token = self.__cipher.encrypt(file_data)  # Encrypt the file data as a Fermet's token format
        fragments = self._fragment_bytes(token)
        file_uuid = str(uuid.uuid4())

        encrypted_file = EncryptedFile(
            uuid=file_uuid,
            user_id=user_id,
            key=self.__key,
            created_at=str(int(datetime.now(timezone.utc).timestamp())),
            fragments=fragments
        )

        return encrypted_file
    
    def _defragment_bytes(self, fragments: list[FileFragment]) -> bytes:
        """
        Combine the fragments into a single byte string. The fragments are sorted by their index to ensure the correct order.

        Args:
            fragments (list[FileFragment]): The list of fragments.

        Returns:
            bytes: The defragmented data.
        """
        return b"".join(frag.data for frag in sorted(fragments, key=lambda f: f.index))

    def decrypt(self, data: list[FileFragment] | bytes) -> bytes:
        """
        Decrypt a file. If the passed data is fragmented, the fragments are combined into a single byte string and then decrypted.

        Args:
            data (list[FileFragment] | bytes): The list of fragments to be decrypted.
        
        Returns:
            bytes: The decrypted file data.
        """
        if isinstance(data, list):
            data = self._defragment_bytes(data)

        return self.__cipher.decrypt(data)
