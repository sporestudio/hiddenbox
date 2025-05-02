from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from lib.crypto import Crypto
import io


@asynccontextmanager
async def lifespan(app: FastAPI):
    crypto = Crypto(redis_url="redis://localhost:6379")
    app.state.crypto = crypto
    yield
    await crypto.close()
    # Close the connection to Redis when the app shuts down
    # (optional, if you want to ensure cleanup)
# ——————————————————————————————————————————


app = FastAPI(lifespan=lifespan)


# ——————————————————————————————————————————
# Configure CORS for the frontend
# ——————————————————————————————————————————

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 5173 is the default port for Vite
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

# ——————————————————————————————————————————

# Define the upload endpoint
@app.post("/upload")
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    data = await file.read()
    try:
        result = app.state.crypto.encrypt_file(data, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/download/{file_id}")
async def download_file(file_id: str, user_id: str):
    try:
        data = app.state.crypto.decrypt_file(file_id, user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="File not found or not access")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return StreamingResponse(io.BytesIO(data), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={file_id}"})
