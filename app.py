import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.services.analyzer import analyze_text, analyze_url, analyze_image, analyze_qr, analyze_audio

st.set_page_config(page_title="VERITAS — Digital Trust & Safety", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.main {background:#f6f9fd}.block-container{max-width:1180px;padding-top:2rem}
.hero{padding:30px;border-radius:22px;background:linear-gradient(135deg,#071a35,#123b69);color:white;margin-bottom:22px}
.hero h1{margin:0;font-size:44px}.hero p{margin:7px 0 0;color:#d9e8fb;font-size:17px}
.card{background:#fff;border:1px solid #dce7f4;border-radius:18px;padding:20px;margin:10px 0;box-shadow:0 5px 18px rgba(20,50,90,.06)}
.high{color:#b42318;font-size:27px;font-weight:800}.medium{color:#a15c00;font-size:27px;font-weight:800}.low{color:#087443;font-size:27px;font-weight:800}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>VERITAS</h1><p>Understand. Verify. Trust.</p><p>Digital Trust & Safety Platform</p></div>', unsafe_allow_html=True)

mode = st.radio("What would you like to verify?", ["Paste Text", "Check URL", "Upload Image", "Scan QR", "Upload Audio"], horizontal=True)
result = None

if mode == "Paste Text":
    text = st.text_area("Paste suspicious message / email / request", height=220)
    if st.button("🔎 ANALYSE", type="primary"):
        if text.strip(): result = analyze_text(text)
        else: st.warning("Please enter some content first.")

elif mode == "Check URL":
    url = st.text_input("URL")
    context = st.text_area("Optional surrounding message", height=120)
    if st.button("🔎 ANALYSE", type="primary"):
        if url.strip(): result = analyze_url(url, context)
        else: st.warning("Please enter a URL.")

elif mode == "Upload Image":
    f = st.file_uploader("Upload screenshot/image", type=["png","jpg","jpeg","webp"])
    context = st.text_area("Optional context", height=100)
    if f:
        st.image(f, width=500)
        if st.button("🔎 ANALYSE", type="primary"):
            result = analyze_image(f.getvalue(), f.name, f.type, context)

elif mode == "Scan QR":
    f = st.file_uploader("Upload QR image", type=["png","jpg","jpeg","webp"])
    context = st.text_area("Optional context", height=100)
    if f:
        st.image(f, width=350)
        if st.button("🔎 ANALYSE", type="primary"):
            result = analyze_qr(f.getvalue(), f.name, context)

else:
    f = st.file_uploader("Upload audio", type=["wav","mp3","m4a","ogg"])
    context = st.text_area("Optional context", height=100)
    if f:
        st.audio(f)
        st.info("The analyzer accepts audio input; connect a speech-to-text provider for production transcription.")
        if st.button("🔎 ANALYSE", type="primary"):
            result = analyze_audio(f.getvalue(), f.name, f.type, context)

if result:
    st.markdown("---")
    st.subheader("VERITAS ASSESSMENT")
    risk = str(result.get("risk_level", "NEEDS VERIFICATION"))
    cls = "high" if "HIGH" in risk.upper() else "low" if "LOW" in risk.upper() else "medium"
    st.markdown(f'<div class="card"><div class="{cls}">{risk}</div><p>{result.get("summary", "Evidence-based assessment from available signals.")}</p></div>', unsafe_allow_html=True)

    st.subheader("Why?")
    evidence = result.get("evidence", [])
    for item in evidence:
        if isinstance(item, dict): st.markdown(f"- **{item.get('title','Signal')}** — {item.get('detail','')}")
        else: st.markdown(f"- {item}")

    st.subheader("Recommended Action")
    st.success(result.get("recommended_action", "Verify independently before taking a sensitive action."))
    with st.expander("View analysis details"):
        st.json(result)

st.caption("VERITAS — Evidence-based digital trust assessment. Results are assessments, not absolute proof.")
