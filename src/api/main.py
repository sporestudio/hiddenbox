#!/usr/bin/env python3

"""
API Module
----------

This module provides a FastAPI application for uploading and downloading encrypted files.
"""

import io
import os
from functools import lru_cache

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from lib.crypto import Crypto
from lib.datatypes import EncryptedFile, EncryptedResponse, FileFragment
from services.redis_service import RedisService
from services.s3_service import s3Service

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
WEB_URL = os.getenv("WEB_URL")
FERNET_KEY = Fernet.generate_key()

@lru_cache
def get_crypto() -> Crypto:
    """
    Singleton pattern for Crypto service to not regenerate the key
    and server cipher every time.
    """
    if not FERNET_KEY:
        raise ValueError("Fernet Key not set")

    return Crypto(key=FERNET_KEY.enconde())

@lru_cache
def get_redis() -> RedisService:
    """
    Singleton pattern to handle Redis service connections.
    """
    if not REDIS_URL:
        raise ValueError("Redis URL not set")

    return RedisService(url=REDIS_URL)

@lru_cache
def get_s3() -> s3Service:
    """
    Singleton pattern to handle S3 service connections.
    """
    return s3Service()

app = FastAPI()

# CORS middleware to allow requests from the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEB_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ———————————————————-
#   /Endpoints
# ———————————————————-

@app.post("/upload", response_model=EncryptedResponse)
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    crypto: Crypto = Depends(get_crypto),
    redis: RedisService = Depends(get_redis),
    s3: s3Service = Depends(get_s3)
) -> EncryptedResponse:
    """
    Upload a file, encrypt it, and store its metadata and fragments in Redis.
    The file is fragmented into smaller chunks for storage.

    Args:
        user_id (str): The user ID of the owner.
        file (UploadFile): The file to be uploaded and encrypted.
        crypto (Crypto): The Crypto service for encryption.
        redis (RedisService): The Redis service for storing metadata and fragments.

    Returns:
        EncryptedResponse: A response model containing the UUID, user ID, encryption key, creation
                           timestamp, and fragments of the encrypted file.
    """
    data = await file.read()

    try:
        encrypted: EncryptedFile = crypto.encrypt(data, user_id)

        redis.store_metadata(
            file_uuid=encrypted.uuid,
            user_id=encrypted.user_id,
            key=encrypted.key.decode(),
            created_at=encrypted.created_at,
        )

        for fragment in encrypted.fragments:
            s3.store_fragment(encrypted.uuid, fragment.index, fragment.data)

        fragment_idxs = [fragment.index for fragment in encrypted.fragments]
        redis.store_fragments(file_uuid=encrypted.uuid, fragments=fragment_idxs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return EncryptedResponse(
        uuid=encrypted.uuid,
        user_id=encrypted.user_id,
        key=encrypted.key.decode(),
        created_at=encrypted.created_at,
        fragments=fragment_idxs,
    )

@app.get("/download/{file_uuid}")
async def download_file(
    file_uuid: str,
    user_id: str,
    crypto: Crypto = Depends(get_crypto),
    redis: RedisService = Depends(get_redis),
    s3: s3Service = Depends(get_s3)
) -> StreamingResponse:
    """
    Download a file by its UUID. The file is decrypted and streamed back to the client.
    The file is reconstructed from its fragments stored in Redis.

    Args:
        file_uuid (str): The UUID of the file to be downloaded.
        user_id (str): The user ID of the owner.
        crypto (Crypto): The Crypto service for decryption.
        redis (RedisService): The Redis service for retrieving metadata and fragments.

    Returns:
        StreamingResponse: A streaming response containing the decrypted file.
    """
    try:
        meta = redis.get_metadata(file_uuid)

        if not meta:
            raise HTTPException(status_code=404, detail="File not found")

        fragment_idxs = redis.get_fragments(file_uuid)
        fragments = []
        for idx in fragment_idxs:
            data = s3.get_fragment(file_uuid, idx)
            fragments.append(FileFragment(uuid=file_uuid, index=idx, data=data))

        data = crypto.decrypt(fragments)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_uuid}.zip"
        }
    )
