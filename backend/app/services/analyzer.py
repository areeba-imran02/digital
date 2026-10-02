import re
from urllib.parse import urlparse
from .qr_service import decode_qr
from .image_service import inspect_image

URGENT = ["urgent", "immediately", "today", "suspended", "expire", "act now", "last warning", "final notice", "within 24 hours", "within 24 hrs"]
FINANCIAL = ["payment", "pay", "transfer", "fee", "refund", "bank", "card", "wallet", "otp", "pin", "crypto", "deposit", "invoice", "money", "cash"]
CREDENTIALS = ["password", "login", "username", "verification code", "otp", "one-time code", "security code", "passcode", "credential"]
IMPERSONATION = ["bank", "paypal", "microsoft", "google", "support", "police", "government", "delivery", "courier", "account team", "customer service", "admin"]
SENSITIVE_ACTIONS = ["click", "verify", "send", "share", "reply", "download", "install", "transfer", "pay", "login", "confirm"]
SUSPICIOUS_TLDS = {".top", ".click", ".xyz", ".zip", ".mov", ".work", ".support", ".quest"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy"}


def _hits(text, words):
    t = (text or "").lower()
    return [w for w in words if w in t]


def _add_signal(signals, category, title, score, detail, evidence_value=None):
    signals.append({"category": category, "title": title, "score": score, "detail": detail, "value": evidence_value})


def _risk(signals):
    raw = sum(s["score"] for s in signals)
    score = min(100, raw)
    if score >= 60:
        return "HIGH RISK", "red", score
    if score >= 25:
        return "NEEDS VERIFICATION", "amber", score
    return "LOW RISK", "green", score


def _result(signals, *, action, identity, summary, input_type, extracted=None, verification_steps=None):
    level, color, score = _risk(signals)
    evidence = [{k: s[k] for k in ("category", "title", "detail", "value")} for s in signals]
    if verification_steps is None:
        verification_steps = [
            "Find the organisation's official website or app independently rather than following the supplied destination.",
            "Verify the sender, recipient, destination and requested action through a trusted channel.",
            "Do not share passwords, OTPs, PINs or payment details until the request is independently verified.",
        ]
    confidence = "strong evidence" if len(signals) >= 3 else "moderate evidence" if signals else "limited evidence"
    return {
        "assessment": {"level": level, "color": color, "score": score, "confidence": confidence},
        "summary": summary,
        "identity_check": identity,
        "evidence": evidence,
        "recommended_action": action,
        "verification_steps": verification_steps,
        "disclaimer": "This is an evidence-based trust assessment, not absolute proof. Important requests should be independently verified.",
        "input_type": input_type,
        "extracted": extracted or {},
    }


def _text_findings(text):
    findings = []
    groups = [
        ("Urgency", URGENT, "Urgency pressure", 24, "This input uses time pressure or immediate-action language, which can reduce a person's chance to verify a request."),
        ("Financial", FINANCIAL, "Financial request", 24, "This input references money, payment, banking or financial information."),
        ("Credentials", CREDENTIALS, "Credential request", 28, "This input references credentials, authentication codes or account-access information."),
        ("Identity", IMPERSONATION, "Impersonation signal", 18, "This input invokes a trusted organisation, support role or institutional identity."),
    ]
    for category, words, title, score, detail in groups:
        hits = _hits(text, words)
        if hits:
            findings.append((category, title, score, detail, hits))
    action_hits = _hits(text, SENSITIVE_ACTIONS)
    if action_hits:
        findings.append(("Action", "Sensitive action requested", 12, "The input asks the recipient to take an action that could expose money, access or personal information.", action_hits))
    return findings


def analyze_text(text, language="auto"):
    text = (text or "").strip()
    signals = []
    findings = _text_findings(text)
    for category, title, score, detail, hits in findings:
        _add_signal(signals, category, title, score, detail, ", ".join(hits[:5]))

    urls = re.findall(r"https?://[^\s<>\"]+", text, flags=re.I)
    if urls:
        for url in urls[:3]:
            parsed = urlparse(url)
            host = parsed.hostname or "unknown"
            detail = f"A destination was embedded in the message ({host}). The destination should be checked independently before opening it."
            _add_signal(signals, "Destination", "Embedded destination", 16, detail, host)

    if not signals:
        summary = "No strong warning pattern was found in the submitted text. That is limited evidence, not proof that the message is legitimate."
        action = "If the request matters, verify the sender and organisation through a trusted channel before acting."
    elif any(s["title"] == "Credential request" for s in signals):
        summary = "The submitted text contains account-access or authentication language that deserves extra verification."
        action = "Do not share passwords, OTPs or verification codes. Open the relevant service independently and check the request there."
    elif any(s["title"] == "Financial request" for s in signals):
        summary = "The submitted text contains financial language and other signals that can increase the consequences of acting without verification."
        action = "Pause any payment or transfer. Independently verify the recipient and request before sending money."
    elif any(s["title"] == "Urgency pressure" for s in signals):
        summary = "The submitted text uses pressure to encourage quick action. That pattern should be verified before you click, reply or pay."
        action = "Do not act under the stated deadline. Verify the claim through an independently found official channel first."
    else:
        summary = f"VERITAS found {len(signals)} signal(s) in the submitted text and combined them into an evidence-based assessment."
        action = "Pause before acting and independently verify the sender, destination and requested action."

    identity = "The claimed identity cannot be established from text alone. Compare the sender and any organisation claim with independently sourced contact details."
    return _result(signals, action=action, identity=identity, summary=summary, input_type="text", extracted={"urls": urls, "language": language, "matched_signal_count": len(findings)})


def analyze_url(url, context=""):
    raw = (url or "").strip()
    normalized = raw if re.match(r"^[a-zA-Z]+://", raw) else "https://" + raw
    parsed = urlparse(normalized)
    host = (parsed.hostname or "").lower()
    signals = []
    if parsed.scheme != "https":
        _add_signal(signals, "Transport", "Non-HTTPS destination", 18, "The URL does not use HTTPS. Verify the destination before entering information.", parsed.scheme)
    if "@" in parsed.netloc:
        _add_signal(signals, "Structure", "Deceptive URL structure", 28, "The URL contains an @ symbol in its network location, which can obscure the actual destination.", parsed.netloc)
    if len(host) > 45 or host.count("-") >= 3:
        _add_signal(signals, "Hostname", "Unusual hostname", 18, "The hostname is unusually long or heavily segmented. Compare it with the organisation's official domain.", host)
    if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
        _add_signal(signals, "Domain", "High-risk TLD pattern", 22, "The hostname uses a TLD that this local ruleset treats as requiring additional verification.", host)
    if host in SHORTENERS or any(host.endswith("." + x) for x in SHORTENERS):
        _add_signal(signals, "Destination", "Shortened destination", 22, "A URL shortener hides the final destination, so the target cannot be judged from the visible link alone.", host)
    context_hits = _text_findings(context)
    if context_hits and any(k in host for k in ["login", "verify", "secure", "account", "update", "payment"]):
        _add_signal(signals, "Context", "Sensitive action + destination", 24, "The URL and surrounding context both point toward an account, payment or verification action.", host)
    if not signals:
        _add_signal(signals, "Domain", "No obvious lexical warning signal", 5, "No strong warning pattern was found from the URL structure alone. This does not establish legitimacy.", host)
    level, _, _ = _risk(signals)
    summary = f"VERITAS inspected {host or 'the submitted destination'} and its URL structure. The assessment reflects only signals available from the supplied URL and context."
    action = "Do not rely on the link alone. Open the organisation's official site or app manually and verify the request there."
    identity = "A hostname is not proof of identity. Compare this domain with an independently sourced official domain before signing in or paying."
    return _result(signals, action=action, identity=identity, summary=summary, input_type="url", extracted={"normalized_url": normalized, "hostname": host, "context_signal_count": len(context_hits), "assessment_basis": level})


def analyze_image(data, filename, content_type, context=""):
    info = inspect_image(data)
    signals = []
    for category, title, score, detail, hits in _text_findings(context):
        _add_signal(signals, category, title, 20 if score < 28 else 24, detail, ", ".join(hits[:5]))
    ocr = info.get("ocr_text") or ""
    for category, title, score, detail, hits in _text_findings(ocr):
        if not any(s["title"] == title for s in signals):
            _add_signal(signals, f"OCR · {category}", title, min(score, 24), detail + " The signal was found in text extracted from the uploaded image.", ", ".join(hits[:5]))
    if not signals:
        _add_signal(signals, "Image", "No text-based warning signal", 5, "No strong warning pattern was found in the available image text or supplied context.", None)
    summary = f"VERITAS inspected '{filename}' using available image metadata and extracted text."
    action = "Do not treat a screenshot as independent proof. Verify names, amounts, recipients and claims through a trusted independent channel."
    identity = "An image or screenshot cannot independently establish the legitimacy of the person or organisation shown."
    return _result(signals, action=action, identity=identity, summary=summary, input_type="image", extracted={"filename": filename, "content_type": content_type, **info})


def analyze_qr(data, filename, context=""):
    decoded = decode_qr(data)
    if decoded:
        base = analyze_url(decoded[0], context)
        base["input_type"] = "qr"
        base["extracted"]["qr_payload"] = decoded[0]
        base["evidence"].insert(0, {"category": "QR", "title": "QR destination decoded", "detail": f"The QR code resolves to {decoded[0]}. That destination is assessed separately below.", "value": decoded[0]})
        return base
    return _result([{"category": "QR", "title": "Unreadable QR code", "score": 10, "detail": "No destination could be decoded from the uploaded QR image.", "value": None}], action="Do not rely on an unreadable QR image. Ask for the destination in plain text and verify it independently.", identity="No destination could be decoded, so the claimed identity cannot be assessed.", summary="VERITAS could not decode a QR destination from this image.", input_type="qr", extracted={"filename": filename})


def analyze_audio(data, filename, content_type, context=""):
    signals = []
    for category, title, score, detail, hits in _text_findings(context):
        _add_signal(signals, category, title, 20 if score < 28 else 24, detail, ", ".join(hits[:5]))
    if not signals:
        _add_signal(signals, "Audio", "Limited audio evidence", 5, "No transcript was supplied, so the current MVP cannot assess spoken claims beyond the supplied context.", None)
    summary = f"VERITAS received '{filename}'. The current MVP can assess supplied context and metadata; full voice transcription/anti-spoof analysis requires a configured speech/AI provider."
    action = "Do not act on a voice request alone. Independently call or message the claimed person or organisation using a known trusted contact method."
    identity = "Voice alone is not sufficient proof of identity. Independent verification is required for sensitive requests."
    return _result(signals, action=action, identity=identity, summary=summary, input_type="audio", extracted={"filename": filename, "content_type": content_type, "bytes": len(data), "transcription_available": False})
