import os
import sys
import tempfile
from pathlib import Path

# Agregar directorio padre al path para importar speech_converter
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from speech_converter import (
    transcribe_audio,
    transcribe_long_audio,
    synthesize_speech,
    SUPPORTED_LANGUAGES,
)

app = FastAPI(
    title="Speech Converter API",
    description="API para convertir voz a texto y texto a voz usando Google Cloud",
    version="1.0.0",
)

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


class TranscribeResponse(BaseModel):
    text: str
    language: str


class SynthesizeResponse(BaseModel):
    message: str
    language: str
    gender: str


class LanguagesResponse(BaseModel):
    languages: dict


@app.get("/")
def root():
    return {"message": "Speech Converter API - Google Cloud", "docs": "/docs"}


@app.get("/api/languages", response_model=LanguagesResponse)
def get_languages():
    return {"languages": SUPPORTED_LANGUAGES}


@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    language: str = Query(default="es", description="Código del idioma"),
    long: bool = Query(default=False, description="True si el audio dura más de 60 segundos"),
):
    valid_extensions = {".wav", ".mp3", ".flac", ".ogg", ".webm"}
    ext = Path(file.filename).suffix.lower()

    if ext not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {ext}. Válidos: {', '.join(valid_extensions)}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if long:
            result = transcribe_long_audio(tmp_path, language)
        else:
            result = transcribe_audio(tmp_path, language)
        return TranscribeResponse(text=result, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)


@app.post("/api/synthesize")
async def synthesize(request: SynthesizeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Idioma no soportado: {request.language}. Válidos: {', '.join(SUPPORTED_LANGUAGES.keys())}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp_path = tmp.name

    try:
        synthesize_speech(request.text, tmp_path, request.language, request.gender)
        return FileResponse(
            tmp_path,
            media_type="audio/mpeg",
            filename="synthesized.mp3",
            headers={
                "X-Language": request.language,
                "X-Gender": request.gender,
            },
        )
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
