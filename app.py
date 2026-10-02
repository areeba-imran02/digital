import sys
from pathlib import Path
import html
import streamlit as st

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.services.analyzer import analyze_text, analyze_url, analyze_image, analyze_qr, analyze_audio

st.set_page_config(page_title="VERITAS · Digital Trust", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root {
  --ink:#211e1a; --ink-soft:#4c4740; --cream:#f3eee5; --paper:#e9e1d4; --panel:#f7f1e8;
  --line:#d7ccbc; --muted:#766e64; --rust:#c85b3d; --coral:#e57b5f; --gold:#c99a4a;
  --sage:#4d8069; --sage-soft:#dce9df; --amber:#b8782f; --amber-soft:#efe0c8;
  --red:#b84b43; --red-soft:#efd7d2;
}
.stApp { background: radial-gradient(circle at 85% 5%, #ead9c9 0, transparent 28%), linear-gradient(145deg,#f4efe7 0%,#e9e1d5 48%,#f2e7da 100%); color:var(--ink); }
.block-container { max-width:1260px; padding:28px 34px 60px; }
header[data-testid="stHeader"] { background:transparent; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#26221d,#312a24); border-right:1px solid #463c33; }
section[data-testid="stSidebar"] * { color:#eee4d7 !important; }
.brand { display:flex; align-items:center; justify-content:space-between; padding:7px 0 24px; }
.brand-name { font-size:24px; font-weight:900; letter-spacing:2px; }
.brand-chip { border:1px solid #6e5c4c; border-radius:999px; padding:6px 10px; color:#dcc9b4; font-size:11px; letter-spacing:.8px; }
.hero { position:relative; overflow:hidden; border:1px solid #4b4036; border-radius:30px; padding:40px 44px; margin-bottom:22px; background:linear-gradient(135deg,#29231e 0%,#44382e 42%,#7b4c3b 100%); box-shadow:0 24px 60px rgba(58,42,30,.20); }
.hero:after { content:""; position:absolute; width:320px; height:320px; right:-80px; top:-140px; border-radius:50%; background:radial-gradient(circle,#e89a77 0,rgba(232,154,119,.08) 65%,transparent 70%); }
.hero h1 { position:relative; z-index:1; margin:0; color:#f5eadc; font-size:54px; line-height:1; letter-spacing:4px; }
.hero .tag { position:relative; z-index:1; color:#edcbb6; font-size:18px; margin-top:11px; font-weight:700; }
.hero .sub { position:relative; z-index:1; color:#d5c5b5; max-width:700px; margin-top:12px; font-size:14px; line-height:1.6; }
.hero-badge { position:absolute; right:38px; bottom:30px; z-index:2; padding:9px 13px; border-radius:999px; background:#eadbc9; color:#3a2e25; font-size:11px; font-weight:800; letter-spacing:.8px; }
.panel { background:rgba(247,241,232,.78); border:1px solid var(--line); border-radius:22px; padding:22px; box-shadow:0 12px 30px rgba(78,59,41,.08); backdrop-filter:blur(8px); }
.section-title { font-size:13px; text-transform:uppercase; letter-spacing:1.5px; color:#776a5e; font-weight:900; margin-bottom:10px; }
.mode-card { background:#e5dace; border:1px solid #cbbcac; border-radius:18px; padding:16px 18px; color:#2d2823; margin-bottom:16px; }
.stTextInput input, .stTextArea textarea { background:#f8f2e9 !important; border:1px solid #cfc1b1 !important; color:#29241f !important; border-radius:13px !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color:#c46a4e !important; box-shadow:0 0 0 2px rgba(196,106,78,.13) !important; }
.stButton > button { border-radius:13px !important; border:1px solid #b85f45 !important; background:linear-gradient(135deg,#d46d50,#b74e3a) !important; color:#f9eee3 !important; font-weight:850 !important; min-height:46px; box-shadow:0 9px 18px rgba(173,76,53,.17); }
.stButton > button:hover { transform:translateY(-1px); filter:brightness(1.04); }
div[data-baseweb="tab-list"] { gap:7px; background:#ded3c6; padding:7px; border-radius:15px; }
button[data-baseweb="tab"] { color:#554b42 !important; border-radius:10px !important; }
button[data-baseweb="tab"][aria-selected="true"] { background:#493b31 !important; color:#f1e6d9 !important; }
.risk-card { margin-top:18px; border-radius:22px; padding:24px; border:1px solid var(--line); background:#f7f0e6; box-shadow:0 12px 28px rgba(70,50,35,.07); }
.risk-high { border-left:7px solid var(--red); background:linear-gradient(120deg,#f2ddd8,#f7eee7); }
.risk-medium { border-left:7px solid var(--amber); background:linear-gradient(120deg,#f1e3cb,#f7eee4); }
.risk-low { border-left:7px solid var(--sage); background:linear-gradient(120deg,#dfebe1,#f4eee5); }
.risk-kicker { font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:#74695e; font-weight:900; }
.risk-title { font-size:34px; font-weight:950; margin:3px 0 7px; letter-spacing:-.7px; }
.high-text { color:#9e4039; } .medium-text { color:#9b6327; } .low-text { color:#35664f; }
.metric { background:#eee5d9; border:1px solid #d5c7b8; border-radius:16px; padding:15px; text-align:center; min-height:82px; }
.metric .num { font-size:23px; font-weight:900; color:#2b2621; } .metric .lbl { color:#756b61; font-size:10px; letter-spacing:1.1px; font-weight:800; }
.evidence { border:1px solid #d5c7b8; border-radius:16px; padding:16px 17px; margin:10px 0; background:#f6eee4; }
.evidence-title { font-weight:900; color:#302a25; } .evidence-detail { color:#62594f; margin-top:5px; font-size:13px; line-height:1.5; }
.signal { display:inline-block; margin-left:8px; padding:4px 7px; border-radius:999px; background:#e5d9cb; color:#75695e; font-size:10px; font-weight:800; }
.action { background:linear-gradient(135deg,#e2eadf,#d5e4d9); border:1px solid #b8ccb9; border-radius:17px; padding:18px; color:#315342; font-weight:750; line-height:1.55; }
.identity { background:#e7ded2; border:1px solid #d0c1b2; border-radius:17px; padding:16px; color:#51483f; line-height:1.55; }
.empty { text-align:center; padding:38px 20px; border:1px dashed #c5b7a7; border-radius:20px; background:rgba(246,239,230,.58); }
.empty-icon { font-size:34px; color:#b86b51; } .small { color:#7b7167; font-size:12px; }
.footer { margin-top:30px; padding-top:18px; border-top:1px solid #d4c7b9; color:#756b61; font-size:12px; }
</style>
""", unsafe_allow_html=True)

if "result" not in st.session_state: st.session_state.result = None
if "analysis_count" not in st.session_state: st.session_state.analysis_count = 0

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-name">VERITAS</div><div class="brand-chip">TRUST ENGINE</div></div>', unsafe_allow_html=True)
    st.markdown("### Verification modes")
    st.caption("Choose the type of digital content you want to understand. Results are based on the evidence you provide.")
    st.markdown("---")
    st.markdown("**Core principles**")
    st.caption("Understand · Verify · Explain · Act Safely")
    st.markdown("---")
    st.caption(f"Analyses this session: {st.session_state.analysis_count}")

st.markdown('<div class="hero"><div class="hero-badge">EVIDENCE-LED DIGITAL SAFETY</div><h1>VERITAS</h1><div class="tag">Understand. Verify. Trust.</div><div class="sub">A professional trust-assessment workspace for suspicious messages, destinations, screenshots, QR codes and audio requests. VERITAS explains the signals it finds instead of hiding the reasoning behind a single label.</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">What would you like to verify?</div>', unsafe_allow_html=True)
mode = st.radio("Verification mode", ["Message / Email", "Web Address", "Screenshot / Image", "QR Code", "Audio"], horizontal=True, label_visibility="collapsed")

with st.container(border=True):
    if mode == "Message / Email":
        st.markdown('<div class="mode-card"><b>Message / Email analysis</b><br><span class="small">Paste the exact text. VERITAS will identify the language, requested action, identity claims and embedded destinations.</span></div>', unsafe_allow_html=True)
        text = st.text_area("Content", height=210, placeholder="Paste the complete message, email, DM or support request here…", label_visibility="collapsed")
        col1, col2 = st.columns([3,1])
        with col1: st.caption("Tip: include the complete message and any visible URL so the assessment can correlate multiple signals.")
        with col2:
            if st.button("Analyse message", use_container_width=True):
                if text.strip():
                    with st.spinner("Building evidence assessment…"):
                        st.session_state.result = analyze_text(text)
                        st.session_state.analysis_count += 1
                        st.rerun()
                else: st.warning("Paste some content first.")
    elif mode == "Web Address":
        st.markdown('<div class="mode-card"><b>Web address analysis</b><br><span class="small">Inspect the exact URL and, if available, the message that accompanied it.</span></div>', unsafe_allow_html=True)
        url = st.text_input("URL", placeholder="https://example.com/verify", label_visibility="collapsed")
        context = st.text_area("Context", height=105, placeholder="Optional: paste the message that sent you this link…", label_visibility="collapsed")
        if st.button("Analyse destination", use_container_width=True):
            if url.strip():
                with st.spinner("Inspecting destination signals…"):
                    st.session_state.result = analyze_url(url, context); st.session_state.analysis_count += 1; st.rerun()
            else: st.warning("Enter a URL first.")
    elif mode == "Screenshot / Image":
        st.markdown('<div class="mode-card"><b>Screenshot / image analysis</b><br><span class="small">Upload the evidence and add context when the screenshot alone cannot explain the request.</span></div>', unsafe_allow_html=True)
        f = st.file_uploader("Upload image", type=["png","jpg","jpeg","webp"], label_visibility="collapsed")
        context = st.text_area("Context", height=100, placeholder="What were you told about this screenshot?", label_visibility="collapsed")
        if f:
            st.image(f, caption=f.name, width=520)
            if st.button("Analyse image", use_container_width=True):
                with st.spinner("Inspecting image evidence…"):
                    st.session_state.result = analyze_image(f.getvalue(), f.name, f.type, context); st.session_state.analysis_count += 1; st.rerun()
    elif mode == "QR Code":
        st.markdown('<div class="mode-card"><b>QR destination analysis</b><br><span class="small">Upload the QR image. VERITAS decodes the destination and then assesses its URL structure.</span></div>', unsafe_allow_html=True)
        f = st.file_uploader("Upload QR", type=["png","jpg","jpeg","webp"], label_visibility="collapsed")
        context = st.text_area("Context", height=100, placeholder="Optional message or sign where the QR appeared…", label_visibility="collapsed")
        if f:
            st.image(f, caption=f.name, width=380)
            if st.button("Decode & analyse QR", use_container_width=True):
                with st.spinner("Decoding and correlating destination evidence…"):
                    st.session_state.result = analyze_qr(f.getvalue(), f.name, context); st.session_state.analysis_count += 1; st.rerun()
    else:
        st.markdown('<div class="mode-card"><b>Audio request analysis</b><br><span class="small">Upload the audio and provide any context you know. Full transcription/voice analysis can be connected later.</span></div>', unsafe_allow_html=True)
        f = st.file_uploader("Upload audio", type=["wav","mp3","m4a","ogg"], label_visibility="collapsed")
        context = st.text_area("Context", height=100, placeholder="What did the caller/voice note ask you to do?", label_visibility="collapsed")
        if f:
            st.audio(f)
            if st.button("Analyse audio", use_container_width=True):
                with st.spinner("Building audio evidence assessment…"):
                    st.session_state.result = analyze_audio(f.getvalue(), f.name, f.type, context); st.session_state.analysis_count += 1; st.rerun()


def render_result(result):
    assessment = result.get("assessment") or {}
    level = str(assessment.get("level") or "NEEDS VERIFICATION").upper()
    score = int(assessment.get("score") or 0)
    confidence = str(assessment.get("confidence") or "limited evidence")
    summary = result.get("summary") or "The available evidence is limited."
    if "HIGH" in level: css, text_cls = "risk-high", "high-text"
    elif "LOW" in level: css, text_cls = "risk-low", "low-text"
    else: css, text_cls = "risk-medium", "medium-text"
    st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Assessment</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="risk-card {css}"><div class="risk-kicker">VERITAS TRUST ASSESSMENT</div><div class="risk-title {text_cls}">{html.escape(level)}</div><div style="color:#5e554c;line-height:1.55">{html.escape(summary)}</div></div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col, val, label in [(c1,score,"RISK SCORE"),(c2,confidence.upper(),"EVIDENCE STRENGTH"),(c3,len(result.get("evidence") or []),"SIGNALS"),(c4,result.get("input_type","unknown").upper(),"INPUT")]:
        with col: st.markdown(f'<div class="metric"><div class="num">{html.escape(str(val))}</div><div class="lbl">{label}</div></div>', unsafe_allow_html=True)
    left,right = st.columns([1.35,1])
    with left:
        st.markdown("### Evidence found")
        evidence = result.get("evidence") or []
        if evidence:
            for item in evidence:
                title = html.escape(str(item.get("title","Signal"))); detail = html.escape(str(item.get("detail","Relevant signal identified."))); cat = html.escape(str(item.get("category","Evidence")))
                value = item.get("value")
                extra = f'<span class="signal">{html.escape(str(value))}</span>' if value else ''
                st.markdown(f'<div class="evidence"><div class="evidence-title">{title}<span class="signal">{cat}</span>{extra}</div><div class="evidence-detail">{detail}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No evidence signals were produced from the submitted content.")
    with right:
        st.markdown("### Identity check")
        st.markdown(f'<div class="identity">{html.escape(str(result.get("identity_check","Identity cannot be established from the available evidence.")))}</div>', unsafe_allow_html=True)
        st.markdown("### Recommended next step")
        st.markdown(f'<div class="action">{html.escape(str(result.get("recommended_action","Verify independently before taking a sensitive action.")))}</div>', unsafe_allow_html=True)
    steps = result.get("verification_steps") or []
    if steps:
        st.markdown("### Verify safely")
        cols = st.columns(len(steps)) if len(steps) <= 3 else [st.container() for _ in range(3)]
        for i, step in enumerate(steps):
            with cols[i % len(cols)]:
                st.markdown(f'<div class="evidence"><b>{i+1:02d}</b><div class="evidence-detail">{html.escape(str(step))}</div></div>', unsafe_allow_html=True)
    extracted = result.get("extracted") or {}
    with st.expander("View technical evidence", expanded=False):
        st.json(extracted)
    st.caption(result.get("disclaimer","This is an evidence-based trust assessment, not absolute proof."))

if st.session_state.result:
    render_result(st.session_state.result)
else:
    st.markdown('<div class="empty"><div class="empty-icon">◈</div><h3>Ready to assess</h3><p class="small">Submit a message, URL, image, QR code or audio request above. Your result will be generated from the evidence actually found in that input.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="footer">VERITAS · Evidence-based digital trust assessment · Results are guidance, not absolute proof.</div>', unsafe_allow_html=True)
