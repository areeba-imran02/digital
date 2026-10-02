"""Optional AI provider boundary.

The rules engine is the default so the app works without external credentials.
A production provider can implement this interface and return structured evidence.
"""
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def analyze(self, *, input_type: str, text: str = "", image_bytes: bytes | None = None, context: str = "") -> dict:
        raise NotImplementedError

class RulesProvider(AIProvider):
    async def analyze(self, **kwargs):
        return {"provider":"rules","note":"Use backend analyzer for deterministic evidence assessment."}
