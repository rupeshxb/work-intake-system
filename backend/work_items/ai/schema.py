# Pydantic schema that validates and enforces the shape of LLM analysis output.
from enum import Enum

from pydantic import BaseModel, field_validator


class AnalysisCategory(str, Enum):
    DOCUMENT_REQUEST = "DOCUMENT_REQUEST"
    PAYMENT_ISSUE = "PAYMENT_ISSUE"
    ACCOUNT_QUERY = "ACCOUNT_QUERY"
    COMPLIANCE_CHECK = "COMPLIANCE_CHECK"
    OTHER = "OTHER"


class AnalysisPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class AnalysisResult(BaseModel):
    category: AnalysisCategory
    priority: AnalysisPriority
    summary: str
    recommendedAction: str

    @field_validator("summary", "recommendedAction")
    @classmethod
    def max_200_chars(cls, v):
        if len(v) > 200:
            raise ValueError("Field exceeds 200 characters")
        return v
