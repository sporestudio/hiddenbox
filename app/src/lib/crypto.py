#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import hashlib
import psycopg2
import json

def __init__(self, db_connection):
    self.conn = psycopg2.connect(db_connection)

def generate_encryption_key(self):
    """
    Generate a random 32-byte encryption key.
    """
    return os.urandom(32)

