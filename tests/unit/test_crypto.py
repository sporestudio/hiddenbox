#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import pytest
from datetime import datetime, timezone
from cryptography.fernet import Fernet, InvalidToken

from app.backend.src.lib.crypto import Crypto
from app.backend.src.lib.datatypes import FileFragment, EncryptedFile

_BYTES_PER_MB = 1024 * 1024

# ----------------------
# Fixtures
# ----------------------

@pytest.fixture
def key():
    return Fernet.generate_key()

@pytest.fixture
def crypto(key):
    return Crypto(key)

@pytest.fixture
def user_id():
    return "user_id"

@pytest.fixture
def data(request):
    """
    Generate random test data of random size in megabytes. The size range will be defined within the variable size_range.
    """
    size_range = (1.0, 10.0)
    size = getattr(request, "param", None)

    if size is None:
        size = random.uniform(*size_range)

    return os.urandom(int(size * _BYTES_PER_MB))

@pytest.fixture
def token(key, data):
    return Fernet(key).encrypt(data)

@pytest.fixture
def fragments(crypto, token):
    return crypto._fragment_token(token)

# ----------------------
# Tests
# ----------------------

def test_encrypted_file_datatype_is_valid(crypto, data, user_id):
    """
    Ensure that encrypt_file returns an EncryptedFile with all expected types and attributes
    """
    encrypted_data = crypto.encrypt_file(data, user_id)

    assert isinstance(encrypted_data, EncryptedFile)
    assert isinstance(encrypted_data.uuid, str)
    assert isinstance(encrypted_data.user_id, str)
    assert isinstance(encrypted_data.key, bytes)
    assert isinstance(encrypted_data.created_at, str)
    assert isinstance(encrypted_data.fragments, list)

def test_fragment_file_datatype_is_valid(fragments):
    """
    Check that each generated fragment is a valid FileFragment with correct types and indices
    """
    assert isinstance(fragments, list)
    assert len(fragments) > 0

    for f in fragments:
        assert isinstance(f, FileFragment)
        assert isinstance(f.uuid, str)
        assert isinstance(f.data, bytes)
        assert isinstance(f.index, int)
        assert 0 <= f.index < len(fragments)

def test_fragments_has_correct_size(fragments, crypto):
    """
    Verify that all fragments are sized correctly, with only the last one potentially smaller
    """
    for f in fragments[:-1]:
        assert len(f.data) == crypto._FRAGMENT_SIZE

    assert len(fragments[-1].data) <= crypto._FRAGMENT_SIZE

def test_encrypt_then_decrypt_restores_original_data(crypto, data, user_id):
    """
    Ensure that data remains the same after encrypting and decrypting
    """
    encrypted_data = crypto.encrypt_file(data, user_id)
    decrypted_data = crypto.decrypt_fragmented_file(encrypted_data.fragments)
    assert decrypted_data == data

def test_encrypted_file_metadata_is_correct(crypto, data, user_id, key):
    """
    Validate that metadata in the EncryptedFile is accurate
    """
    encrypted_data = crypto.encrypt_file(data, user_id)
    assert encrypted_data.user_id == user_id
    assert encrypted_data.key == key

def test_created_at_timestamp_is_close_to_now(crypto, data, user_id):
    """
    Ensure created_at timestamp is within 1 second of current UTC time
    """
    encrypted_data = crypto.encrypt_file(data, user_id)
    now_ts = int(datetime.now(timezone.utc).timestamp())
    created_at_ts = int(encrypted_data.created_at)
    assert abs(now_ts - created_at_ts) <= 1

def test_encrypt_empty_file(crypto, user_id):
    """
    Ensure that encrypting and decrypting an empty byte string works correctly
    """
    empty_file = b""
    encrypted_data = crypto.encrypt_file(empty_file, user_id)
    decrypted_data = crypto.decrypt_fragmented_file(encrypted_data.fragments)

    assert decrypted_data == empty_file

@pytest.mark.parametrize("data", [20.0, 40.0], indirect=True)
def test_encrypt_large_file_generates_multiple_fragments(crypto, user_id, data):
    """
    Check that encrypting large files results in multiple fragments as expected
    """
    encrypted_file = crypto.encrypt_file(data, user_id)

    assert len(encrypted_file.fragments) > 1

def test_decryption_works_even_fragment_disordered(crypto, user_id, data):
    """
    Confirm that decryption still works when fragments are provided in a different order
    """
    encrypted_file = crypto.encrypt_file(data, user_id)

    reversed_fragments = list(reversed(encrypted_file.fragments))
    decrypted_data = crypto.decrypt_fragmented_file(reversed_fragments)
    assert decrypted_data == data

def test_decryption_fails_on_modified_fragment(crypto, user_id, data):
    """
    Verify that tampering with a fragment causes decryption to fail with an InvalidToken error
    """
    encrypted_file = crypto.encrypt_file(data, user_id)
    fragments = encrypted_file.fragments

    corrupted_data = bytearray(fragments[0].data)
    corrupted_data[0] ^= 0xFF
    fragments[0].data = bytes(corrupted_data)

    with pytest.raises(InvalidToken):
        crypto.decrypt_fragmented_file(fragments)
