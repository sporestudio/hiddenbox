#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
from dataclasses import dataclass

@dataclass
class FileFragment:
    """
    Represents a fragment of a file.

    Attributes:
        uuid (str): A unique identifier for the fragment.
        data (bytes): The fragment data.
        index (int): The index of the fragment in the original file.
    """
    uuid: str
    data: bytes
    index: int

@dataclass
class EncryptedFile:
    """
    Represents an encrypted file.

    Attributes:
        uuid (str): A unique identifier for the file.
        user_id (str): The user ID of the owner.
        key (str): The key used to encrypt the file.
        created_at (str): The timestamp when the file was created.
        fragments (list[FileFragment]): A list of fragments of the encrypted file.
    """
    uuid: str
    user_id: str
    key: bytes
    created_at: str
    fragments: List[FileFragment]
