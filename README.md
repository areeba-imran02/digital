# VERITAS — Digital Trust & Safety Platform

A complete hackathon-ready full-stack source project for the supplied VERITAS concept: **Understand. Verify. Trust.**

## What is included

- React + Vite frontend with polished VERITAS interface
- FastAPI backend with structured API schemas
- Text analysis: urgency, financial, credential and impersonation signals
- URL analysis: HTTPS, hostname, shortened links, TLD and structural checks
- Image workflow with metadata and optional OCR boundary
- QR decoding with OpenCV
- Audio workflow with a provider-ready transcription boundary
- Explainable evidence cards, trust score and safer-action guidance
- Identity-consistency assessment wording
- Configurable CORS and upload limits
- Environment templates
- Dockerfiles + Docker Compose
- Modular AI-provider boundary so an external multimodal model can be added without replacing the product architecture

The project implements the supplied product story: **User Input → Multimodal Analysis → Identity Check → Risk Analysis → Evidence Engine → Trust Assessment → Explanation → Safer Action.**

## 1. Run locally — Windows

### Backend

```powershell
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend API: http://localhost:8000
Swagger docs: http://localhost:8000/docs

### Frontend

Open a second terminal:

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

Open the Vite address shown in the terminal, normally http://localhost:5173.

## 2. Run locally — macOS/Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Second terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## 3. Docker

From the project root:

```bash
docker compose up --build
```

Frontend: http://localhost:5173
Backend: http://localhost:8000/docs

## 4. Optional OCR

The image service automatically uses OCR if `pytesseract` and a Tesseract installation are available. Install the Python package from `backend/requirements-ocr.txt` and install Tesseract separately for your OS.

Without OCR, the image flow still works using metadata and supplied context.

## 5. API endpoints

- `GET /api/health`
- `POST /api/analyze/text`
- `POST /api/analyze/url`
- `POST /api/analyze/image`
- `POST /api/analyze/qr`
- `POST /api/analyze/audio`

FastAPI generates interactive OpenAPI documentation at `/docs`.

## 6. AI provider integration

The default rules engine deliberately requires no API key. For a production multimodal implementation, keep the provider behind `backend/app/services/ai_provider.py` and return structured evidence instead of free-form text.

Recommended production flow:

1. Sanitize and classify input.
2. Extract OCR / QR / URL artifacts.
3. Send only necessary content to the selected model/provider.
4. Require structured JSON evidence.
5. Validate model output with server-side rules.
6. Store minimal audit metadata.
7. Show the user evidence + uncertainty + safer action.

Never expose provider secrets in the React frontend.

## 7. Production hardening checklist

- Authentication / authorization
- Rate limiting
- Malware scanning for uploads
- File signature validation, not only MIME types
- Object storage with short-lived access
- Encryption at rest and in transit
- Retention/deletion controls
- Abuse monitoring
- Human review path for high-impact cases
- Provider timeout/retry/circuit breaker logic
- Structured audit logs without storing unnecessary sensitive content
- Security headers and restrictive CORS

## 8. Important product limitation

VERITAS provides evidence-based decision support. A score is not proof that content is fraudulent or legitimate. The UI therefore emphasizes **why**, **evidence**, **identity consistency**, and **how to verify safely**.
