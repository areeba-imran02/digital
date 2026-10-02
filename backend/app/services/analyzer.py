import re
from urllib.parse import urlparse
from .qr_service import decode_qr
from .image_service import inspect_image

URGENT = ["urgent", "immediately", "today", "suspended", "expire", "act now", "last warning", "final notice", "within 24 hours"]
FINANCIAL = ["payment", "pay", "transfer", "fee", "refund", "bank", "card", "wallet", "otp", "pin", "crypto", "deposit", "invoice"]
CREDENTIALS = ["password", "login", "username", "verification code", "otp", "one-time code", "security code", "passcode"]
IMPERSONATION = ["bank", "paypal", "microsoft", "google", "support", "police", "government", "delivery", "courier", "account team"]
SUSPICIOUS_TLDS = {".top", ".click", ".xyz", ".zip", ".mov", ".work", ".support", ".quest"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy"}


def _hits(text, words):
    t = text.lower()
    return [w for w in words if w in t]


def _text_signals(text):
    groups = [("Urgency", URGENT), ("Financial request", FINANCIAL), ("Credential request", CREDENTIALS), ("Impersonation context", IMPERSONATION)]
    return [(label, _hits(text, words)) for label, words in groups if _hits(text, words)]


def _risk(signals):
    raw = sum(s for _, _, s in signals)
    score = min(100, raw)
    if score >= 60: level, color = "HIGH RISK", "red"
    elif score >= 25: level, color = "NEEDS VERIFICATION", "yellow"
    else: level, color = "LOW RISK", "green"
    return level, color, score


def _result(signals, *, action, identity, summary, input_type, extracted=None):
    level, color, score = _risk(signals)
    evidence = []
    for category, title, severity in signals:
        evidence.append({"category": category, "title": title, "detail": _DETAILS.get(title, "A relevant warning signal was identified in the submitted evidence."), "severity": min(5, severity // 10 + 1)})
    steps = [
        "Find the organisation's official website or app independently.",
        "Verify the sender, recipient, destination and requested action through a trusted channel.",
        "Do not share passwords, OTPs, PINs or payment details until independently verified.",
    ]
    return {"assessment":{"level":level,"color":color,"score":score,"confidence":"evidence-based"},"summary":summary,"identity_check":identity,"evidence":evidence,"recommended_action":action,"verification_steps":steps,"disclaimer":"This is an evidence-based trust assessment, not absolute proof. Important requests should be independently verified.","input_type":input_type,"extracted":extracted or {}}

_DETAILS = {
    "Urgency pressure": "The content pressures the recipient to act quickly or immediately, a common social-engineering pattern.",
    "Financial request": "The content references money, payment, transfer, banking or financial credentials.",
    "Credential request": "The content asks for authentication secrets or access-related information.",
    "Impersonation signal": "The content appears to invoke a trusted organisation, role or support identity.",
    "Suspicious destination": "The destination has lexical or structural characteristics that warrant independent verification.",
    "Shortened destination": "A URL shortener hides the final destination, reducing transparency before a click.",
    "Non-HTTPS destination": "The URL does not use HTTPS, so transport security cannot be assumed.",
    "Deceptive URL structure": "The URL contains a structure that can be used to obscure the apparent destination.",
    "High-risk TLD pattern": "The hostname uses a TLD that the local ruleset treats as requiring additional verification.",
    "Unusual hostname": "The hostname has unusual length or character patterns and should be independently checked.",
    "QR destination decoded": "A QR code was decoded and its destination can now be assessed separately.",
}


def analyze_text(text, language="auto"):
    signals = []
    for label, hits in _text_signals(text):
        title = {"Urgency":"Urgency pressure","Financial request":"Financial request","Credential request":"Credential request","Impersonation context":"Impersonation signal"}[label]
        signals.append((label, title, 22 if label != "Impersonation context" else 18))
    urls = re.findall(r"https?://[^\s<>\"]+", text, flags=re.I)
    if urls:
        signals.append(("Destination", "Suspicious destination", 18))
    return _result(signals, action="Pause before clicking, paying, sharing credentials, or replying. Verify the claimed organisation through an independently found official channel.", identity="The claimed identity cannot be established from text alone; identity consistency requires independent evidence.", summary="VERITAS analyzed language, requested actions and embedded destinations for evidence-based warning signals.", input_type="text", extracted={"urls":urls,"language":language})


def analyze_url(url, context=""):
    normalized = url if re.match(r"^[a-zA-Z]+://", url) else "https://" + url
    parsed = urlparse(normalized)
    host = (parsed.hostname or "").lower()
    signals = []
    if parsed.scheme != "https": signals.append(("Transport", "Non-HTTPS destination", 18))
    if "@" in parsed.netloc: signals.append(("Structure", "Deceptive URL structure", 28))
    if len(host) > 45 or host.count("-") >= 3: signals.append(("Hostname", "Unusual hostname", 18))
    if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS): signals.append(("Domain", "High-risk TLD pattern", 22))
    if host in SHORTENERS or any(host.endswith("."+x) for x in SHORTENERS): signals.append(("Destination", "Shortened destination", 22))
    if any(k in host for k in ["login", "verify", "secure", "account", "update"]):
        if _hits(context, CREDENTIALS + FINANCIAL): signals.append(("Context", "Credential/payment context", 24))
    if not signals: signals.append(("Domain", "No obvious lexical warning signal", 5))
    return _result(signals, action="Do not rely on the link alone. Open the organisation's official site or app manually and verify the request there.", identity="The hostname is not proof of the claimed organisation. Compare it with an independently sourced official domain.", summary=f"Destination analyzed: {host or 'unknown host'}.", input_type="url", extracted={"normalized_url":normalized,"hostname":host})


def analyze_image(data, filename, content_type, context=""):
    info = inspect_image(data)
    signals = []
    for label, hits in _text_signals(context):
        title = {"Urgency":"Urgency pressure","Financial request":"Financial request","Credential request":"Credential request","Impersonation context":"Impersonation signal"}[label]
        signals.append((label, title, 20))
    if info.get("ocr_text"):
        for label, hits in _text_signals(info["ocr_text"]):
            title = {"Urgency":"Urgency pressure","Financial request":"Financial request","Credential request":"Credential request","Impersonation context":"Impersonation signal"}[label]
            if not any(x[1] == title for x in signals): signals.append((label, title, 20))
    return _result(signals, action="Do not treat a screenshot as independent proof. Verify names, amounts, recipients and claims through a trusted independent channel.", identity="A screenshot cannot independently establish the legitimacy of the person or organisation shown.", summary="The image was inspected for available text and context. Visual evidence should be independently verified before a sensitive action.", input_type="image", extracted={"filename":filename,"content_type":content_type,**info})


def analyze_qr(data, filename, context=""):
    decoded = decode_qr(data)
    if decoded:
        base = analyze_url(decoded[0], context)
        base["input_type"] = "qr"
        base["extracted"]["qr_payload"] = decoded[0]
        base["evidence"].insert(0, {"category":"QR","title":"QR destination decoded","detail":"The QR code resolved to a destination that can now be inspected independently.","severity":2})
        return base
    return _result([("QR","Unreadable QR code",10)], action="Do not scan again on an untrusted device. Ask for the destination in plain text and verify it independently.", identity="No destination could be decoded, so the claimed identity cannot be assessed.", summary="VERITAS could not decode a QR destination from this image.", input_type="qr", extracted={"filename":filename})


def analyze_audio(data, filename, content_type, context=""):
    signals = []
    for label, hits in _text_signals(context):
        title = {"Urgency":"Urgency pressure","Financial request":"Financial request","Credential request":"Credential request","Impersonation context":"Impersonation signal"}[label]
        signals.append((label, title, 20))
    return _result(signals, action="Do not act on a voice request alone. Independently call or message the claimed person or organisation using a known trusted contact method.", identity="Voice alone is not sufficient proof of identity. Independent verification is required for sensitive requests.", summary="The audio workflow is ready for transcription/voice-analysis providers; the current MVP uses supplied context plus metadata.", input_type="audio", extracted={"filename":filename,"content_type":content_type,"bytes":len(data)})
