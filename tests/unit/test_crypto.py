#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
from datetime import datetime, timezone
from app.backend.src.lib.crypto import Crypto
from cryptography.fernet import Fernet, InvalidToken
from app.backend.src.lib.datatypes import FileFragment, EncryptedFile

class TestCrypto:
    def setup_method(self):
        """Initialize common test data before each test method."""
        self.key = Fernet.generate_key()
        self.crypto = Crypto(self.key)
        self.bytes = self._generate_test_data(2.5)
        self.user_id = "test_user_id"
        self.token = Fernet(self.key).encrypt(self.bytes)
        self.fragments = self.crypto._fragment_token(self.token)

    def _generate_test_data(self, mb_size: float = 1.0) -> bytes:
        return os.urandom(int(mb_size * 1024 * 1024))

    def test_encrypted_file_datatype_is_valid(self):
        """Ensure that encrypt_file returns an EncryptedFile with all expected types and attributes."""
        encrypted_data = self.crypto.encrypt_file(self.bytes, self.user_id)

        assert isinstance(encrypted_data, EncryptedFile)
        assert isinstance(encrypted_data.uuid, str)
        assert isinstance(encrypted_data.user_id, str)
        assert isinstance(encrypted_data.key, bytes)
        assert isinstance(encrypted_data.created_at, str)
        assert isinstance(encrypted_data.fragments, list)

    def test_fragment_file_datatype_is_valid(self):
        """Check that each generated fragment is a valid FileFragment with correct types and indices."""
        assert isinstance(self.fragments, list)
        assert len(self.fragments) > 0

        for f in self.fragments:
            assert isinstance(f, FileFragment)
            assert isinstance(f.uuid, str)
            assert isinstance(f.data, bytes)
            assert isinstance(f.index, int)
            assert 0 <= f.index < len(self.fragments)

    def test_fragments_has_correct_size(self):
        """Verify that all fragments are sized correctly, with only the last one potentially smaller."""
        for f in self.fragments[:-1]:
            assert len(f.data) == self.crypto._FRAGMENT_SIZE
        
        assert len(self.fragments[-1].data) <= self.crypto._FRAGMENT_SIZE

    def test_values_are_correct(self):
        """Test full encryption-decryption cycle and validate metadata integrity."""
        encrypted_data = self.crypto.encrypt_file(self.bytes, self.user_id)
        decrypted_data = self.crypto.decrypt_fragmented_file(encrypted_data.fragments)

        assert decrypted_data == self.bytes
        assert encrypted_data.user_id == self.user_id
        assert encrypted_data.key == self.crypto._Crypto__key

        now_ts = int(datetime.now(timezone.utc).timestamp())
        created_at_ts = int(encrypted_data.created_at)
        assert abs(now_ts - created_at_ts) <= 1

        for f in encrypted_data.fragments:
            assert 0 <= f.index < len(encrypted_data.fragments)

    def test_encrypt_empty_file(self):
        """Ensure that encrypting and decrypting an empty byte string works correctly."""
        empty_file = b""
        encrypted_data = self.crypto.encrypt_file(empty_file, self.user_id)
        decrypted_data = self.crypto.decrypt_fragmented_file(encrypted_data.fragments)

        assert decrypted_data == empty_file

    def test_encrypt_large_file_generates_multiple_fragments(self):
        """Check that encrypting a large file results in multiple fragments as expected."""
        file_data = self._generate_test_data(5)
        encrypted_file = self.crypto.encrypt_file(file_data, self.user_id)

        assert len(encrypted_file.fragments) > 1

    def test_decryption_works_even_fragment_disordered(self):
        """Confirm that decryption still works when fragments are provided in a different order."""
        file_data = self._generate_test_data(1.0)
        encrypted_file = self.crypto.encrypt_file(file_data, self.user_id)

        reversed_fragments = list(reversed(encrypted_file.fragments))
        decrypted_data = self.crypto.decrypt_fragmented_file(reversed_fragments)
        assert decrypted_data == file_data

    def test_decryption_fails_on_modified_fragment(self):
        """Verify that tampering with a fragment causes decryption to fail with an InvalidToken error."""
        file_data = self._generate_test_data(1.0)
        encrypted_file = self.crypto.encrypt_file(file_data, self.user_id)
        fragments = encrypted_file.fragments

        corrupted_data = bytearray(fragments[0].data)
        corrupted_data[0] ^= 0xFF
        fragments[0].data = bytes(corrupted_data)

        with pytest.raises(InvalidToken):
            self.crypto.decrypt_fragmented_file(fragments)
