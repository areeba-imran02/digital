"""Optional generative reasoning layer for VERITAS.

The deterministic analyzer always runs first. When OPENAI_API_KEY is supplied
through Streamlit secrets/environment, this module adds input-specific natural
language reasoning and explanations. No key is stored in the repository.
"""
import json
import os
import re
from typing import Any


def _clean_json(text: str) -> dict[str, Any] | None:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except Exception:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            return None
        try:
            value = json.loads(match.group(0))
            return value if isinstance(value, dict) else None
        except Exception:
            return None


def available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def reason_about_input(*, input_type: str, content: str, context: str = "", base_result: dict | None = None) -> dict | None:
    """Return a structured, input-specific reasoning layer or None when unavailable."""
    if not available():
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = os.getenv("VERITAS_AI_MODEL", "gpt-6-luna")
        base = base_result or {}
        prompt = f"""
You are VERITAS, an evidence-led digital trust and safety analyst.
Analyze ONLY the supplied user content and the deterministic signals. Do not invent facts,
URLs, sender identities, organizations, or evidence that is not present.

Input type: {input_type}
User content:
{content[:18000]}

User context:
{context[:6000]}

Deterministic preliminary result:
{json.dumps(base, ensure_ascii=False)[:12000]}

Return ONLY valid JSON with exactly these keys:
summary: concise 2-4 sentence explanation specific to this input
identity_check: specific assessment of the identity claim, or explain why it cannot be established
why_flagged: array of 1-6 strings, each tied to visible evidence
recommended_action: one concrete safer next action
verification_steps: array of 2-5 concrete steps
user_answer: a natural-language answer to the user's likely question about this content
language: "en" unless the user clearly used another language; then use that language

Important: distinguish "no evidence found" from "safe". Never claim certainty from limited evidence.
"""
        response = client.responses.create(
            model=model,
            instructions="Return JSON only. Be precise, conservative, and directly reference the submitted content.",
            input=prompt,
            max_output_tokens=1200,
        )
        return _clean_json(getattr(response, "output_text", ""))
    except Exception:
        # The app remains usable if the provider is unavailable or the key/model is misconfigured.
        return None
