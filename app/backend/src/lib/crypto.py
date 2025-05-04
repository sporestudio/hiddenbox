#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid 
from typing import List
from datetime import datetime, timezone   
from .datatypes import FileFragment, EncryptedFile
from cryptography.fernet import Fernet

class Crypto:
    _FRAGMENT_SIZE = 1024 ** 2 # 1MB

    def __init__(self, key):
        self.__key = key 
        self.__cipher = Fernet(self.__key)

    def _fragment_token(self, token: bytes) -> List[FileFragment]:
        """
        Fragment a tokenized (encrypted) file into smaller chunks. Each chunk is represented as a dictionary.

        Args:
            token (bytes): The file encrypted using Fernet's token format.

        Returns:
            List[FileFragment]: A list of file fragments. To see FileFragment attributes refer to `datatypes` module documentation.
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

    def encrypt_file(self, file_data: bytes, user_id: str) -> EncryptedFile:
        """
        Encrypt a file and associate it with the user's ID. The file is fragmented into smaller chunks.
        
        Args:
            file_data (bytes): The file data to be encrypted.
            user_id (str): The user ID of the owner.
        
        Returns:
            EncryptedFile: An object representing the encrypted file (data and metadata included). To see EncryptedFile attributes refer to `datatypes` module documentation.
        """
        token = self.__cipher.encrypt(file_data)  # Encrypt the file data as a Fermet's token format
        fragments = self._fragment_token(token)
        file_uuid = str(uuid.uuid4())

        encrypted_file = EncryptedFile(
            uuid=file_uuid,
            user_id=user_id,
            key=self.__key,
            created_at=str(int(datetime.now(timezone.utc).timestamp())),
            fragments=fragments
        )

        return encrypted_file
    
    def decrypt_fragmented_file(self, fragments: List[FileFragment]) -> bytes:
        """
        Decrypt a fragmented file. The fragments are combined into a single byte string and then decrypted.

        Args:
            fragments (List[FileFragment]): The list of fragments to be decrypted.
        
        Returns:
            bytes: The decrypted file data.
        """
        sorted_fragments = sorted(fragments, key=lambda x: x.index)  # Sort fragments by index
        token = b"".join([frag.data for frag in sorted_fragments])

        return self.__cipher.decrypt(token)
