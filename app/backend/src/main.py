import os, io, uuid, time
from functools import lru_cache
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lib.crypto import Crypto
from cryptography.fernet import Fernet
from lib.redis_service import RedisService
from lib.datatypes import FileFragment, EncryptedFile


# ——————————————————————————————---
#   Dependencies and environment
# ——————————————————————————————---
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
WEB_URL = os.getenv("WEB_URL")
FERNET_KEY = Fernet.generate_key()

@lru_cache()
def get_crypto() -> Crypto:
    """
    Singleton pattern for Crypto service to not regenerate the key
    and server cipher every time.
    """
    if not FERNET_KEY:
        raise RunTimeError("Fernet Key not set")
    return Crypto(key=FERNET_KEY.enconde())

@lru_cache()
def get_redis() -> RedisService:
    """
    Singleton pattern to handle Redis service connections.
    """
    if not REDIS_URL:
        raise RunTimeError("Redis URL not set")
    return RedisService(url=REDIS_URL)
    

# ——————————————————————————————————————————
#   Create the app and add CORS middleware
# ——————————————————————————————————————————
app = FastAPI()

# CORS middleware to allow requests from the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEB_URL],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)


# ——————————————————————————————
#   Input/Output models
# ——————————————————————————————
class EncryptResponse(BaseModel):
    """
    Response model for the encryption endpoint.
    Contains the UUID, user ID, encryption key, creation timestamp,
    and fragments of the encrypted file.

    Attributes:
        uuid (str): The UUID of the encrypted file.
        user_id (str): The user ID of the owner.
        key (str): The encryption key used for the file.
        created_at (str): The timestamp when the file was created.
        fragments (List[FileFragment]): A list of fragments of the encrypted file.
    """
    uuid: str
    user_id: str
    key: str
    created_at: str
    fragments: List[FileFragment]


# ———————————————————-
#   /Endpoints
# ———————————————————-
@app.post("/upload", response_model=EncryptResponse)
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    crypto: Crypto = Depends(get_crypto),
    redis: RedisService = Depends(get_redis),
) -> EncryptResponse:
    """
    Upload a file, encrypt it, and store its metadata and fragments in Redis.
    The file is fragmented into smaller chunks for storage.

    Args:
        user_id (str): The user ID of the owner.
        file (UploadFile): The file to be uploaded and encrypted.
        crypto (Crypto): The Crypto service for encryption.
        redis (RedisService): The Redis service for storing metadata and fragments. 

    Returns:
        EncryptResponse: A response model containing the UUID, user ID, encryption key, creation timestamp, and fragments of the encrypted file.
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

        fragments_to_save = [
            FileFragment(uuid=str(uuid.uuid4()), fragment=fragment)
            for fragment in encrypted.fragments
        ]

        redis.store_fragments(file_uuid=encrypted.uuid, fragments=fragments_to_save)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   

    return EncryptResponse(
        uuid=encrypted.uuid,
        user_id=encrypted.user_id,
        key=encrypted.key.decode(),
        created_at=encrypted.created_at,
        fragments=fragments_to_save,
    )


@app.get("/download/{file_uuid}")
async def download_file(
    file_uuid: str,
    user_id: str,
    crypto: Crypto = Depends(get_crypto),
    redis: RedisService = Depends(get_redis),
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
        
        raw = redis.get_fragments(file_uuid)
        fragments = [
            FileFragment(uuid=file_uuid, index=idx, data=frag) for idx, frag in raw
        ]

        data = cryto.decrypt(fragments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_uuid}.zip"
        }
    )
