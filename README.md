# VERITAS — Streamlit Digital Trust & Safety

A polished Streamlit MVP for evidence-based assessment of suspicious messages, URLs, screenshots, QR codes and audio requests.

## Streamlit deployment

- Main file: `app.py`
- Python: 3.11
- Dependencies: `requirements.txt`
- Do not commit API keys. Add deployment secrets in Streamlit Cloud when needed.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The current MVP performs local evidence-based analysis. External AI/speech providers can be connected later through the backend service layer.
