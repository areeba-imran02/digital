import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models.schemas import TextRequest, UrlRequest
from .services.analyzer import analyze_text, analyze_url, analyze_image, analyze_qr, analyze_audio

load_dotenv()
app = FastAPI(title="VERITAS API", version="1.0.0", description="Digital Trust & Safety analysis API")
origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
MAX_BYTES = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024

def _validate_upload(data):
    if not data: raise HTTPException(400, "Empty upload")
    if len(data) > MAX_BYTES: raise HTTPException(413, "File exceeds configured upload limit")

@app.get("/api/health")
def health(): return {"status":"ok","service":"veritas-api","version":"1.0.0"}

@app.post("/api/analyze/text")
def text_analysis(req: TextRequest): return analyze_text(req.text, req.language)

@app.post("/api/analyze/url")
def url_analysis(req: UrlRequest): return analyze_url(req.url, req.context)

@app.post("/api/analyze/image")
async def image_analysis(file: UploadFile = File(...), context: str = Form("")):
    data = await file.read(); _validate_upload(data)
    return analyze_image(data, file.filename or "image", file.content_type or "application/octet-stream", context)

@app.post("/api/analyze/qr")
async def qr_analysis(file: UploadFile = File(...), context: str = Form("")):
    data = await file.read(); _validate_upload(data)
    return analyze_qr(data, file.filename or "qr", context)

@app.post("/api/analyze/audio")
async def audio_analysis(file: UploadFile = File(...), context: str = Form("")):
    data = await file.read(); _validate_upload(data)
    return analyze_audio(data, file.filename or "audio", file.content_type or "audio/*", context)
