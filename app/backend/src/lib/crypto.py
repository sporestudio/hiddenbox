#!/usr/bin/env python

"""
Crypto Module
-------------

This module provides a Crypto class that allows you to encrypt and decrypt files,
as well as fragment and defragment the encrypted data. The encrypted files are associated
with a user ID and stored as a list of FileFragment objects. Each fragment contains
the fragment's index and data. The module also provides a method to generate a unique
identifier for each file.
"""

import uuid
from datetime import UTC, datetime

from cryptography.fernet import Fernet

from .datatypes import EncryptedFile, FileFragment

class Crypto:
    _FRAGMENT_SIZE = 1024 * 1024 # 1MB

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        This method ensures that the Crypto class is a singleton.
        It creates a new instance of the class if one does not already exist.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, key: bytes):
        self.__key = key
        self.__cipher = Fernet(self.__key)

    def _reinit_if_key_changes(self, key: bytes) -> None:
        """
        Reinitialize the cipher if the key changes.

        Args:
            key (bytes): The encryption key.
        """
        if key != self.__key:
            self.__key = key
            self.__cipher = Fernet(self.__key)

    def _fragment_bytes(self, token: bytes) -> list[FileFragment]:
        """
        Fragment a tokenized (encrypted) file into smaller chunks. Each chunk is represented as a dictionary.

        Args:
            token (bytes): The file encrypted using Fernet's token format.

        Returns:
            list[FileFragment]: A list of file fragments.
                                To see FileFragment attributes refer to `datatypes` module documentation.
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

    def encrypt(self, file_data: bytes, user_id: str, key: bytes) -> EncryptedFile:
        """
        Encrypt a file and associate it with the user's ID. The file is fragmented into smaller chunks.

        Args:
            file_data (bytes): The file data to be encrypted.
            user_id (str): The user ID of the owner.
            key (bytes): The encryption key to be used.

        Returns:
            EncryptedFile: An object representing the encrypted file (data and metadata included).
                           To see EncryptedFile attributes refer to `datatypes` module documentation.
        """
        self._reinit_if_key_changes(key)

        token = self.__cipher.encrypt(file_data)  # Encrypt the file data as a Fermet's token format
        fragments = self._fragment_bytes(token)
        file_uuid = str(uuid.uuid4())

        encrypted_file = EncryptedFile(
            uuid=file_uuid,
            user_id=user_id,
            key=self.__key,
            created_at=str(int(datetime.now(UTC).timestamp())),
            fragments=fragments
        )

        return encrypted_file

    def _defragment_bytes(self, fragments: list[FileFragment]) -> bytes:
        """
        Combine the fragments into a single byte string. The fragments are sorted by their index
        to ensure the correct order.

        Args:
            fragments (list[FileFragment]): The list of fragments.

        Returns:
            bytes: The defragmented data.
        """
        return b"".join(frag.data for frag in sorted(fragments, key=lambda f: f.index))

    def decrypt(self, data: list[FileFragment] | bytes, key: bytes) -> bytes:
        """
        Decrypt a file. If the passed data is fragmented, the fragments are combined into a single byte
        string and then decrypted.

        Args:
            data (list[FileFragment] | bytes): The list of fragments to be decrypted.
            key (bytes): The encryption key to be used.

        Returns:
            bytes: The decrypted file data.
        """
        self._reinit_if_key_changes(key)

        if isinstance(data, list):
            data = self._defragment_bytes(data)

        return self.__cipher.decrypt(data)
