from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl

RiskColor = Literal["green", "yellow", "red"]

class Evidence(BaseModel):
    category: str
    title: str
    detail: str
    severity: int = Field(ge=1, le=5)

class Assessment(BaseModel):
    level: Literal["LOW RISK", "NEEDS VERIFICATION", "HIGH RISK"]
    color: RiskColor
    score: int = Field(ge=0, le=100)
    confidence: str

class AnalysisResult(BaseModel):
    assessment: Assessment
    summary: str
    identity_check: str
    evidence: list[Evidence]
    recommended_action: str
    verification_steps: list[str]
    disclaimer: str
    input_type: str
    extracted: dict = {}

class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50000)
    language: str = "auto"

class UrlRequest(BaseModel):
    url: str = Field(min_length=3, max_length=4096)
    context: str = Field(default="", max_length=20000)
