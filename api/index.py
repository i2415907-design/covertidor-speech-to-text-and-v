import os
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Agregar directorio al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from speech_converter import (
    transcribe_audio,
    transcribe_long_audio,
    synthesize_speech,
    SUPPORTED_LANGUAGES,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SynthesizeRequest(BaseModel):
    text: str
    language: str = "es"
    gender: str = "neutral"


@app.get("/api/languages")
def get_languages():
    return {"languages": SUPPORTED_LANGUAGES}


@app.post("/api/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Query(default="es"),
    long: bool = Query(default=False),
):
    valid_extensions = {".wav", ".mp3", ".flac", ".ogg", ".webm"}
    ext = Path(file.filename).suffix.lower()

    if ext not in valid_extensions:
        raise HTTPException(status_code=400, detail=f"Formato no soportado: {ext}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if long:
            result = transcribe_long_audio(tmp_path, language)
        else:
            result = transcribe_audio(tmp_path, language)
        return {"text": result, "language": language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)


@app.post("/api/synthesize")
async def synthesize(request: SynthesizeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp_path = tmp.name

    try:
        synthesize_speech(request.text, tmp_path, request.language, request.gender)
        return FileResponse(
            tmp_path,
            media_type="audio/mpeg",
            filename="synthesized.mp3",
        )
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Speech Converter API", "docs": "/docs"}
